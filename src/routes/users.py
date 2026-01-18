from typing import Dict
from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from src.models.user import User, UserCreate, UserRead, UserUpdate
from src.models.deck import Deck

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate):
    """Cria um novo usuário"""
    existing = await User.find_one(User.email == data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado!")
    user = User(
        name=data.name,
        email=data.email,
        password=data.password
    )
    await user.insert()
    return user

@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: PydanticObjectId):
    """Busca um usuário pelo ID"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")
    return user

@router.get("/", response_model=Page[UserRead], status_code=status.HTTP_200_OK)
async def list_users():
    """Retorna todos os usuários com paginação"""
    return await apaginate(User.find_all())

@router.get("/{user_id}/decks/count", response_model=int, status_code=status.HTTP_200_OK)
async def count_user_decks(user_id: PydanticObjectId):
    """Conta quantos decks o usuário tem"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")
    count = await Deck.find(Deck.owner.id == user.id).count()
    return count

@router.get("/{user_id}/decks/count-by-format", status_code=status.HTTP_200_OK)
async def count_user_decks_by_format(user_id: PydanticObjectId) -> Dict[str, int]:
    """Retorna a contagem de decks por formato"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")
    pipeline = [
        {"$match": {"owner.$id": user.id}},
        {"$group": {"_id": "$format", "count": {"$sum": 1}}}
    ]
    
    docs = await Deck.aggregate(pipeline).to_list()

    result: Dict[str, int] = {}
    for doc in docs:
        result[doc["_id"]] = doc["count"]

    return result

@router.get("/{user_id}/decks", response_model=Page[Deck], status_code=status.HTTP_200_OK)
async def list_user_decks(user_id: PydanticObjectId):
    """Lista todos os decks do usuário com paginação"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")

    return await apaginate(Deck.find(Deck.owner.id == user.id))

@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(user_id: PydanticObjectId, updated_user: UserUpdate):
    """Atualiza dados do usuário"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")

    changes = updated_user.model_dump(exclude_unset=True)
    
    if not changes:
        raise HTTPException(400, "Nenhum campo para atualizar")
    
    for key, value in changes.items():
        setattr(user, key, value)
    
    await user.save()
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: PydanticObjectId):
    """Deleta um usuário"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")

    await user.delete()