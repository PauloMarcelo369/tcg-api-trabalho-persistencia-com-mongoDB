from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, EmailStr # Adicione EmailStr se quiser validar email

class User(Document):
    name: str
    email: str
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

class UserCreate(BaseModel):
    name: str = Field(
        ..., 
        title="Nome Completo",
        description="Nome do usuário para exibição",
        min_length=3,
        examples=["João da Silva"]
    )
    email: str = Field( 
        ..., 
        title="E-mail",
        description="Endereço de e-mail único do usuário",
        examples=["joao@email.com"]
    )
    password: str = Field(
        ..., 
        title="Senha",
        description="Senha segura (será criptografada)",
        min_length=6,
        examples=["senhaForte123!"]
    )

class UserUpdate(BaseModel):
    name: Optional[str] = Field(
        None, 
        title="Nome Completo",
        description="Novo nome do usuário",
        examples=["João Editado"]
    )
    email: Optional[str] = Field(
        None, 
        title="E-mail",
        description="Novo e-mail do usuário",
        examples=["novoemail@email.com"]
    )
    password: Optional[str] = Field(
        None, 
        title="Senha",
        description="Nova senha",
        examples=["novaSenha123"]
    )

class UserRead(BaseModel):
    id: PydanticObjectId = Field(..., title="ID do Usuário")
    name: str = Field(..., title="Nome")
    email: str = Field(..., title="E-mail")
    created_at: datetime = Field(..., title="Data de Criação")