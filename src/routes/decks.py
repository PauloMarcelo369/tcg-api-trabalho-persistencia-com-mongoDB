from src.models.card import Card
from datetime import date
from src.models.deck import Deck, AddCardsRequest, DeckCreate, DeckUpdate, DeckResponse
from src.models.user import User
from src.models.enums.enums import DeckFormat 
from fastapi_pagination import Page
from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime
from beanie import PydanticObjectId
from collections import Counter

import re

from fastapi_pagination.ext.beanie import apaginate

router = APIRouter(
    prefix="/decks",
    tags=["Decks"]
)

async def add_cards_to_deck_helper(deck, card_ids: list[str]):
    """
    Adiciona cartas a um deck existente garantindo:
    - apenas 1 cópia de cada carta
    - existência das cartas
    """
    existing_ids = {str(c.id) for c in deck.cards}  

    for cid in card_ids:
        cid_str = str(cid)

        if cid_str in existing_ids:
            raise HTTPException(
                status_code=400,
                detail=f"A carta {cid_str} já está no deck"
            )


        card = await Card.get(PydanticObjectId(cid_str))
        if not card:
            raise HTTPException(
                status_code=400,
                detail=f"Carta {cid_str} não encontrada"
            )

        deck.cards.append(card)
        existing_ids.add(cid_str)  

    await deck.save()
    return deck


async def remove_card_from_deck_helper(deck, card_id: str):
    """
    Remove uma carta de um deck existente.
    """
    card_str = str(card_id)
    
    card_in_deck = next((c for c in deck.cards if str(c.id) == card_str), None)
    if not card_in_deck:
        raise HTTPException(
            status_code=404,
            detail=f"A carta {card_str} não está no deck"
        )

    deck.cards.remove(card_in_deck)
    
    await deck.save()
    return deck



@router.post("/", response_model=DeckResponse, status_code=201)
async def create_deck(data: DeckCreate):
    owner = await User.get(data.owner_id)
    if not owner:
        raise HTTPException(404, "Usuário não encontrado")

    existing_deck = await Deck.find_one({
    "name": data.name, 
    "owner.$id": PydanticObjectId(owner.id) 
  })
    if existing_deck:
        raise HTTPException(
            status_code=400,
            detail=f"Você já possui um deck com o nome '{data.name}'"
        )
    
    if existing_deck:
        return

    deck = Deck(
        name=data.name,
        format=data.format,
        owner=owner,
        cards=[]
    )
    await deck.insert()

    return DeckResponse(
        id=str(deck.id),
        name=deck.name,
        format=deck.format,
        created_at=deck.created_at,
        owner=deck.owner,
        cards_ids=[]
    )


@router.post("/{deck_id}/add_cards", response_model=DeckResponse)
async def add_cards_to_deck(deck_id: str, data: AddCardsRequest):
    deck = await Deck.get(PydanticObjectId(deck_id), fetch_links=True)
    if not deck:
        raise HTTPException(404, "Deck não encontrado")

    deck = await add_cards_to_deck_helper(deck, data.card_ids)

    return DeckResponse(
        id=str(deck.id),
        name=deck.name,
        format=deck.format,
        created_at=deck.created_at,
        owner=deck.owner,
        cards_ids=[str(card.id) for card in deck.cards]
    )



@router.post("/{deck_id}/remove_card/{card_id}", response_model=DeckResponse)
async def remove_card(deck_id: str, card_id : str):
    deck = await Deck.get(PydanticObjectId(deck_id), fetch_links=True)
    if not deck:
        raise HTTPException(404, "Deck não encontrado")

    deck = await remove_card_from_deck_helper(deck, card_id)

    return DeckResponse(
        id=str(deck.id),
        name=deck.name,
        format=deck.format,
        created_at=deck.created_at,
        owner=deck.owner,
        cards_ids=[str(c.id) for c in deck.cards]
    )



@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(deck_id: str, data: DeckUpdate):
    deck = await Deck.get(deck_id, fetch_links=True)
    if not deck:
        raise HTTPException(404, "Deck não encontrado")

    if data.name is not None:
        deck.name = data.name

    if data.format is not None:
        deck.format = data.format

    if data.card_ids is not None:
        cards = await Card.find(
            {"_id": {"$in": [PydanticObjectId(cid) for cid in data.card_ids]}}
        ).to_list()

        if len(cards) != len(data.card_ids):
            raise HTTPException(400, "Uma ou mais cartas não foram encontradas")

        deck.cards = cards

    await deck.save()

    return DeckResponse(
        id=str(deck.id),
        name=deck.name,
        format=deck.format,
        created_at=deck.created_at,
        owner=deck.owner,  
        cards_ids=[str(card.id) for card in deck.cards]
    )

@router.get("/", response_model=Page[Deck])
async def list_decks():
    page = await apaginate(Deck.find())

    for deck in page.items:
        await deck.fetch_all_links()

    return page


@router.get("/by-format/{format}", response_model=Page[Deck])
async def decks_by_format(format: DeckFormat):
    page = await apaginate(
        Deck.find(
            {"format": format}
        )
    )
    for deck in page.items:
        await deck.fetch_all_links()

    return page


@router.get("/by-date", response_model=Page[Deck])
async def decks_by_date(
    start: datetime,
    end: datetime
):
    page = await apaginate(
        Deck.find(
            {
                "created_at": {
                    "$gte": start,
                    "$lte": end
                }
            }
        )
    )

    for deck in page.items:
        await deck.fetch_all_links()

    return page



@router.get("/search", response_model=Page[Deck])
async def search_decks(
    query: str = Query(..., min_length=2)
):
    """
    Retorna uma lista paginada de Decks cujo nome contenha a string de consulta.
    """
    regex = re.compile(query, re.IGNORECASE)

    page = await apaginate(
        Deck.find(
            {"name": {"$regex": regex}}
        )
    )

    for deck in page.items:
        await deck.fetch_all_links()

    return page




@router.get("/{deck_id}/cards", response_model=Page[Card])
async def get_deck_cards(deck_id: str):
    deck = await Deck.get(deck_id)
    
    if not deck:
        raise HTTPException(404, "Deck não encontrado")

    card_ids = [c.ref.id for c in deck.cards]

    return await apaginate(
        Card.find({"_id": {"$in": card_ids}})
    )



@router.get("/count")
async def count_collections():
    total = await Deck.find_all().count()
    return {"total": total}




@router.get("/stats/by-format")
async def decks_by_format_stats():
    pipeline = [
        {
            "$group": {
                "_id": "$format",
                "total": {"$sum": 1}
            }
        }
    ]

    return await Deck.aggregate(pipeline).to_list()