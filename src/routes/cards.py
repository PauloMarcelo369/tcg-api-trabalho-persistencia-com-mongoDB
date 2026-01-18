from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query
from beanie import PydanticObjectId
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

    try:
        card = Card(
            name=data.name,
            type=data.type,
            rarity=data.rarity,
            text=data.text,
            collection=collection
        )
        await card.insert()
        return CardRead(**card.model_dump(), collection=card.collection)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar carta: {e}")

@router.get("/{card_id}", response_model=CardRead, status_code=status.HTTP_200_OK)
async def get_card_by_id(card_id: PydanticObjectId):
    """Busca carta por ID"""
    card = await Card.get(card_id)
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

@router.get("/", response_model=List[CardRead], status_code=status.HTTP_200_OK)
async def list_cards(skip: int = 0, limit: int = 10):
    """Lista todas as cartas com paginação"""
    cards = await Card.find_all().skip(skip).limit(limit).to_list()
    return [CardRead(**c.model_dump(), collection=c.collection) for c in cards]

@router.get("/search/{name}", response_model=List[CardRead], status_code=status.HTTP_200_OK)
async def search_card_by_name(name: str, skip: int = 0, limit: int = Query(10, le=50)):
    """Busca cartas por nome (Case Insensitive)"""
    cards = await Card.find(
        {"name": {"$regex": name, "$options": "i"}}
    ).skip(skip).limit(limit).to_list()
    
    return [CardRead(**c.model_dump(), collection=c.collection) for c in cards]

@router.get("/collection/{collection_id}", response_model=List[CardRead], status_code=status.HTTP_200_OK)
async def get_cards_by_collection(collection_id: PydanticObjectId, skip: int = 0, limit: int = Query(10, le=50)):
    """Busca todas as cartas de uma coleção específica"""
    collection = await Collection.get(collection_id)
    if not collection:
        raise HTTPException(404, f"Collection com ID {collection_id} não existe!")
    cards = await Card.find(Card.collection.id == collection.id).skip(skip).limit(limit).to_list()
    return [CardRead(**c.model_dump(), collection=c.collection) for c in cards]


@router.get("/stats/by-collection", status_code=status.HTTP_200_OK)
async def cards_per_collection_stats():
    """Estatísticas: Contagem de cartas por coleção (com nome da coleção)"""
    pipeline = [
        {"$group": {"_id": "$collection.$id", "total_cards": {"$sum": 1}}},
        {"$lookup": {
            "from": "collections",
            "localField": "_id",
            "foreignField": "_id",
            "as": "collection_info"
        }},
        {"$unwind": "$collection_info"},
        {"$sort": {"total_cards": -1}},
        {"$project": {
            "collection_name": "$collection_info.name", 
            "total_cards": 1, 
            "_id": 0
        }}
    ]
    
    return await Card.aggregate(pipeline).to_list()

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