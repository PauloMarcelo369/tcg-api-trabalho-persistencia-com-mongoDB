import re
from fastapi import APIRouter, HTTPException, status, Query
from beanie import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from src.models.card import Card, CardCreate, CardRead, CardUpdate
from src.models.collection import Collection

router = APIRouter(prefix="/cards", tags=["Cards"])

@router.post("/", response_model=CardRead, status_code=status.HTTP_201_CREATED)
async def create_card(data: CardCreate):
    """Cria uma nova carta"""
    existing = await Card.find_one(Card.name == data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Carta com esse nome já existe!")
    
    collection = await Collection.get(data.collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection com ID {data.collection_id} não existe!")
    card = Card(
        name=data.name,
        type=data.type,
        rarity=data.rarity,
        text=data.text,
        collection=collection
    )
    await card.insert()
    
    return CardRead(**card.model_dump(), collection=card.collection)

@router.get("/{card_id}", response_model=CardRead, status_code=status.HTTP_200_OK)
async def get_card_by_id(card_id: PydanticObjectId):
    """Busca carta por ID"""
    card = await Card.get(card_id, fetch_links=True)
    if not card:
        raise HTTPException(404, f"Carta com ID {card_id} não existe!")
    return CardRead(**card.model_dump(), collection=card.collection)

@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(card_id: PydanticObjectId):
    """Deleta uma carta"""
    card = await Card.get(card_id)
    if not card:
        raise HTTPException(404, f"Carta com ID {card_id} não existe!")
    
    await card.delete()

@router.put("/{card_id}", response_model=CardRead, status_code=status.HTTP_200_OK)
async def update_card(card_id: PydanticObjectId, updated_card: CardUpdate):
    """Atualiza uma carta"""
    card = await Card.get(card_id)
    if not card:
        raise HTTPException(404, f"Carta com ID {card_id} não existe!")

    card_dict = updated_card.model_dump(exclude_unset=True)
    if not card_dict:
        raise HTTPException(400, "Nenhum campo para atualizar")

    if 'collection_id' in card_dict:
        new_collection = await Collection.get(card_dict['collection_id'])
        if not new_collection:
            raise HTTPException(404, f"Collection com ID {card_dict['collection_id']} não existe!")
        card.collection = new_collection
        del card_dict['collection_id'] 

    for key, value in card_dict.items():
        setattr(card, key, value)
    
    await card.save()
    return CardRead(**card.model_dump(), collection=card.collection)

@router.get("/", response_model=Page[CardRead], status_code=status.HTTP_200_OK)
async def list_cards():
    """Lista todas as cartas com paginação automática"""
    return await apaginate(Card.find_all(fetch_links=True))

@router.get("/search", response_model=Page[CardRead], status_code=status.HTTP_200_OK)
async def search_cards(
    query: str = Query(..., min_length=2, description="Texto para busca no nome da carta")
):
    """
    Busca cartas por nome (Case Insensitive) com paginação.
    Substitui a rota /search/{name} para manter padrão Query param.
    """
    regex = re.compile(query, re.IGNORECASE)
    
    return await apaginate(
        Card.find(
            {"name": {"$regex": regex}},
            fetch_links=True
        )
    )

@router.get("/stats/by-rarity", status_code=status.HTTP_200_OK)
async def cards_by_rarity_stats():
    """Estatísticas: Contagem por raridade"""
    pipeline = [
        {"$group": {"_id": "$rarity", "total_cards": {"$sum": 1}}},
        {"$sort": {"total_cards": -1}},
        {"$project": {"rarity": "$_id", "total_cards": 1, "_id": 0}}
    ]
    return await Card.aggregate(pipeline).to_list()

@router.get("/stats/by-type", status_code=status.HTTP_200_OK)
async def cards_by_type_stats():
    """Estatísticas: Contagem por tipo"""
    pipeline = [
        {"$group": {"_id": "$type", "total_cards": {"$sum": 1}}},
        {"$sort": {"total_cards": -1}},
        {"$project": {"type": "$_id", "total_cards": 1, "_id": 0}}
    ]
    return await Card.aggregate(pipeline).to_list()