from typing import Dict
from fastapi import APIRouter, HTTPException, status, Path
from beanie import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from src.models.user import User, UserCreate, UserRead, UserUpdate
from src.models.deck import Deck

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/", 
    response_model=UserRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo usuário",
    description="Registra um novo usuário no sistema. O e-mail deve ser único.",
    responses={
        201: {"description": "Usuário criado com sucesso"},
        400: {"description": "Erro de Negócio: E-mail já cadastrado"},
        422: {"description": "Erro de Validação: Dados inválidos (ex: senha curta, email inválido)"}
    }
)
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

@router.get(
    "/{user_id}", 
    response_model=UserRead, 
    status_code=status.HTTP_200_OK,
    summary="Buscar usuário por ID",
    description="Retorna os detalhes públicos de um usuário específico.",
    responses={
        200: {"description": "Usuário encontrado"},
        404: {"description": "Usuário não encontrado"},
        422: {"description": "ID inválido"}
    }
)
async def get_user_by_id(
    user_id: PydanticObjectId = Path(..., description="ID único do usuário (ObjectID)")
):
    """Busca um usuário pelo ID"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")
    return user

@router.get(
    "/", 
    response_model=Page[UserRead], 
    status_code=status.HTTP_200_OK,
    summary="Listar todos os usuários",
    description="Retorna uma lista paginada de todos os usuários cadastrados.",
    responses={
        200: {"description": "Lista de usuários recuperada com sucesso"}
    }
)
async def list_users():
    """Retorna todos os usuários com paginação"""
    return await apaginate(User.find_all())

@router.put(
    "/{user_id}", 
    response_model=UserRead, 
    status_code=status.HTTP_200_OK,
    summary="Atualizar usuário",
    description="Atualiza nome, email ou senha de um usuário existente.",
    responses={
        200: {"description": "Usuário atualizado com sucesso"},
        400: {"description": "Erro de Requisição: Nenhum dado enviado para atualização"},
        404: {"description": "Usuário não encontrado"},
        422: {"description": "Erro de Validação"}
    }
)
async def update_user(
    user_id: PydanticObjectId = Path(..., description="ID do usuário a ser atualizado"), 
    updated_user: UserUpdate = None
):
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

@router.delete(
    "/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir usuário",
    description="Remove permanentemente um usuário do banco de dados.",
    responses={
        204: {"description": "Usuário removido com sucesso"},
        404: {"description": "Usuário não encontrado"},
        422: {"description": "ID inválido"}
    }
)
async def delete_user(
    user_id: PydanticObjectId = Path(..., description="ID do usuário a ser excluído")
):
    """Deleta um usuário"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")

    await user.delete()