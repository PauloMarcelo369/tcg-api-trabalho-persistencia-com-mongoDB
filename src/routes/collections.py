from datetime import date, datetime
from fastapi import APIRouter, HTTPException, status, Query
from beanie import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
import re

from src.models.collection import (
    Collection,
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse
)
from src.models.card import Card

router = APIRouter(
    prefix="/collections",
    tags=["Collections"]
)


@router.get(
    "/search", 
    response_model=Page[Collection],
    status_code=status.HTTP_200_OK,
    summary="Buscar coleções por nome",
    description="Retorna uma lista paginada de collections cujo nome contenha a string de consulta.",
    responses={
        200: {"description": "Busca realizada com sucesso"},
        422: {"description": "Erro de Validação: Query muito curta"}
    }
)
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

@router.get(
    "/count",
    status_code=status.HTTP_200_OK,
    summary="Contar coleções",
    description="Retorna o número total de coleções cadastradas no sistema.",
    responses={
        200: {"description": "Contagem retornada com sucesso"}
    }
)
async def count_collections():
    total = await Collection.find_all().count()
    return {"total": total}

@router.get(
    "/filter/by-year", 
    response_model=Page[Collection],
    status_code=status.HTTP_200_OK,
    summary="Filtrar por ano",
    description="Retorna coleções lançadas em um ano específico.",
    responses={
        200: {"description": "Filtro aplicado com sucesso"},
        422: {"description": "Ano inválido (fora do intervalo 1900-2100)"}
    }
)
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

@router.get(
    "/stats/by-year",
    status_code=status.HTTP_200_OK,
    summary="Estatísticas: Por Ano",
    description="Agrupa e conta quantas coleções foram lançadas em cada ano.",
    responses={
        200: {"description": "Estatísticas geradas com sucesso"}
    }
)
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

@router.get(
    "/stats/with-cards",
    status_code=status.HTTP_200_OK,
    summary="Estatísticas: Volume de Cartas",
    description="Retorna a lista de coleções indicando quantas cartas existem em cada uma.",
    responses={
        200: {"description": "Relatório gerado com sucesso"}
    }
)
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

@router.get(
    "/", 
    response_model=Page[Collection],
    status_code=status.HTTP_200_OK,
    summary="Listar todas as coleções",
    description="Retorna todas as coleções com paginação.",
    responses={
        200: {"description": "Lista recuperada com sucesso"}
    }
)
async def list_collections():
    return await apaginate(
        Collection.find_all()
    )


@router.post(
    "/", 
    response_model=CollectionResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Criar coleção",
    description="Cadastra uma nova coleção no banco de dados.",
    responses={
        201: {"description": "Coleção criada com sucesso"},
        422: {"description": "Erro de Validação: Campos obrigatórios faltando"},
        500: {"description": "Erro interno ao confirmar criação"}
    }
)
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

@router.get(
    "/{collection_id}", 
    response_model=CollectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar coleção por ID",
    description="Retorna os detalhes de uma coleção específica.",
    responses={
        200: {"description": "Coleção encontrada"},
        404: {"description": "Coleção não encontrada"},
        422: {"description": "ID inválido"}
    }
)
async def get_collection(collection_id: str):
    collection = await Collection.get(collection_id)
    if not collection:
        raise HTTPException(404, "Collection não encontrada")

    return CollectionResponse(
        id=str(collection.id),
        name=collection.name,
        release_date=collection.release_date
    )

@router.get(
    "/{collection_id}/cards", 
    response_model=Page[Card],
    status_code=status.HTTP_200_OK,
    summary="Listar cartas da coleção",
    description="Retorna todas as cartas pertencentes a uma coleção específica.",
    responses={
        200: {"description": "Cartas recuperadas com sucesso"},
        404: {"description": "Coleção não encontrada"},
        422: {"description": "ID inválido"}
    }
)
async def get_collection_cards(collection_id: str):
    collection = await Collection.get(collection_id, fetch_links=True)

    if not collection:
        raise HTTPException(404, "Collection não encontrada")

    return await apaginate(
        Card.find({"collection.$id": collection.id})
    )

@router.put(
    "/{collection_id}", 
    response_model=CollectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar coleção",
    description="Atualiza o nome ou data de lançamento da coleção.",
    responses={
        200: {"description": "Coleção atualizada com sucesso"},
        404: {"description": "Coleção não encontrada"},
        422: {"description": "Dados de atualização inválidos"}
    }
)
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

@router.delete(
    "/{collection_id}",
    status_code=status.HTTP_200_OK,
    summary="Excluir coleção",
    description="Remove uma coleção do sistema.",
    responses={
        200: {"description": "Coleção removida com sucesso"},
        404: {"description": "Coleção não encontrada"},
        422: {"description": "ID inválido"}
    }
)
async def delete_collection(collection_id: str):
    collection = await Collection.get(collection_id)
    if not collection:
        raise HTTPException(404, "Collection não encontrada")

    await collection.delete()
    return {"message": "Collection removida com sucesso"}