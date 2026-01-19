import re
from fastapi import APIRouter, HTTPException, status, Query, Path
from beanie import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from src.models.card import Card, CardCreate, CardRead, CardUpdate
from src.models.collection import Collection

router = APIRouter(prefix="/cards", tags=["Cards"])

@router.post(
    "/", 
    response_model=CardRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova carta",
    description="Cria uma carta associada a uma coleção existente. O nome da carta deve ser único.",
    responses={
        400: {"description": "Carta com esse nome já existe"},
        404: {"description": "Coleção informada não encontrada"}
    }
)
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

@router.get(
    "/{card_id}", 
    response_model=CardRead, 
    status_code=status.HTTP_200_OK,
    summary="Buscar carta por ID",
    description="Retorna os detalhes de uma carta específica.",
    responses={
        404: {"description": "Carta não encontrada"}
    }
)
async def get_card_by_id(
    card_id: PydanticObjectId = Path(..., description="ID da carta a ser buscada")
):
    """Busca carta por ID"""
    card = await Card.get(card_id, fetch_links=True)
    if not card:
        raise HTTPException(404, f"Carta com ID {card_id} não existe!")
    return CardRead(**card.model_dump(), collection=card.collection)

@router.delete(
    "/{card_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir carta",
    responses={
        404: {"description": "Carta não encontrada"}
    }
)
async def delete_card(
    card_id: PydanticObjectId = Path(..., description="ID da carta a ser deletada")
):
    """Deleta uma carta"""
    card = await Card.get(card_id)
    if not card:
        raise HTTPException(404, f"Carta com ID {card_id} não existe!")
    
    await card.delete()

@router.put(
    "/{card_id}", 
    response_model=CardRead, 
    status_code=status.HTTP_200_OK,
    summary="Atualizar carta",
    description="Atualiza campos de uma carta. Se o collection_id for alterado, a carta é movida para outra coleção.",
    responses={
        404: {"description": "Carta ou nova Coleção não encontrada"},
        400: {"description": "Nenhum dado enviado para atualização"}
    }
)
async def update_card(
    card_id: PydanticObjectId = Path(..., description="ID da carta a ser atualizada"), 
    updated_card: CardUpdate = None
):
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

@router.get(
    "/", 
    response_model=Page[CardRead], 
    status_code=status.HTTP_200_OK,
    summary="Listar todas as cartas",
    description="Retorna lista paginada de todas as cartas do sistema."
)
async def list_cards():
    """Lista todas as cartas com paginação automática"""
    return await apaginate(Card.find_all(fetch_links=True))

@router.get(
    "/search", 
    response_model=Page[CardRead], 
    status_code=status.HTTP_200_OK,
    summary="Buscar cartas por nome",
    description="Realiza uma busca textual (case-insensitive) no nome das cartas."
)
async def search_cards(
    query: str = Query(..., min_length=2, description="Texto parcial para busca no nome da carta (ex: 'dragon')")
):
    """
    Busca cartas por nome (Case Insensitive) com paginação.
    """
    regex = re.compile(query, re.IGNORECASE)
    
    return await apaginate(
        Card.find(
            {"name": {"$regex": regex}},
            fetch_links=True
        )
    )

@router.get(
    "/stats/by-rarity", 
    status_code=status.HTTP_200_OK,
    summary="Estatísticas: Por Raridade",
    description="Retorna a contagem total de cartas agrupadas por raridade."
)
async def cards_by_rarity_stats():
    """Estatísticas: Contagem por raridade"""
    pipeline = [
        {"$group": {"_id": "$rarity", "total_cards": {"$sum": 1}}},
        {"$sort": {"total_cards": -1}},
        {"$project": {"rarity": "$_id", "total_cards": 1, "_id": 0}}
    ]
    return await Card.aggregate(pipeline).to_list()

@router.get(
    "/stats/by-type", 
    status_code=status.HTTP_200_OK,
    summary="Estatísticas: Por Tipo",
    description="Retorna a contagem total de cartas agrupadas por tipo."
)
async def cards_by_type_stats():
    """Estatísticas: Contagem por tipo"""
    pipeline = [
        {"$group": {"_id": "$type", "total_cards": {"$sum": 1}}},
        {"$sort": {"total_cards": -1}},
        {"$project": {"type": "$_id", "total_cards": 1, "_id": 0}}
    ]
    return await Card.aggregate(pipeline).to_list()