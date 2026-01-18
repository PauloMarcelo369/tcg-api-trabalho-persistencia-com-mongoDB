from datetime import date
from fastapi import APIRouter, HTTPException,  status, Query
from beanie import PydanticObjectId
from src.models.collection import Collection
from src.models.card import Card
import re
from fastapi_pagination import Page
from datetime import datetime

from fastapi_pagination.ext.beanie import apaginate

from src.models.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse
)

router = APIRouter(
    prefix="/collections",
    tags=["Collections"]
)

@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(data : CollectionCreate):
    """
    Cria uma nova coleção.
    """
    collection = Collection(**data.model_dump())
    await collection.insert()

    collection_inserted = await Collection.get(collection.id, fetch_links=True)

    if not collection_inserted:
        raise HTTPException(status_code=500, detail="Erro ao criar coleção")
    
    return CollectionResponse(
        id=str(collection.id),
        name=collection.name,
        release_date=collection.release_date
    )

@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(collection_id: str, data: CollectionUpdate):
    collection = await Collection.get(collection_id)
    if not collection:
        raise HTTPException(404, "Collection não encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(collection, field, value)

    await collection.save()

    return CollectionResponse(
        id=str(collection.id),
        name=collection.name,
        release_date=collection.release_date
    )

@router.delete("/{collection_id}")
async def delete_collection(collection_id: str):
    collection = await Collection.get(collection_id)
    if not collection:
        raise HTTPException(404, "Collection não encontrada")

    await collection.delete()
    return {"message": "Collection removida com sucesso"}


@router.get("/search", response_model=Page[Collection])
async def search_collections(
    query: str = Query(..., min_length=2, description="Texto para busca no nome da coleção")
):
    """
    Retorna uma lista paginada de collections cujo nome contenha a string de consulta.
    """
    regex = re.compile(query, re.IGNORECASE)

    return await apaginate(
        Collection.find(
            {"name": {"$regex": regex}}
        )
    )

@router.get("/count")
async def count_collections():
    total = await Collection.find_all().count()
    return {"total": total}

@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: str):
    collection = await Collection.get(collection_id)
    if not collection:
        raise HTTPException(404, "Collection não encontrada")

    return CollectionResponse(
        id=str(collection.id),
        name=collection.name,
        release_date=collection.release_date
    )

@router.get("/", response_model=Page[Collection])
async def list_collections():
    return await apaginate(
        Collection.find_all()
    )

@router.get("/{collection_id}/cards", response_model=Page[Card])
async def get_collection_cards(collection_id: str):
    collection = await Collection.get(collection_id, fetch_links=True)

    if not collection:
        raise HTTPException(404, "Collection não encontrada")

    return await apaginate(
        Card.find({"collection.$id": collection.id})
    )


@router.get("/filter/by-year", response_model=Page[Collection])
async def filter_by_year(
    year: int = Query(..., ge=1900, le=2100)
):
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)

    return await apaginate(
        Collection.find({
            "release_date": {
                "$gte": start,
                "$lt": end
            }
        })
    )

@router.get("/stats/by-year")
async def count_by_year():
    pipeline = [
        {
            "$group": {
                "_id": {"$year": "$release_date"},
                "total": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]

    return await Collection.aggregate(pipeline).to_list()

@router.get("/stats/with-cards")
async def collections_with_card_count():
    pipeline = [
        {
            "$lookup": {
                "from": "cards",
                "localField": "_id",
                "foreignField": "collection.$id",
                "as": "cards"
            }
        },
        {
            "$project": {
                "_id": {"$toString": "$_id"},  
                "name": 1,
                "total_cards": {"$size": "$cards"}
            }
        }
    ]

    return await Collection.aggregate(pipeline).to_list()
