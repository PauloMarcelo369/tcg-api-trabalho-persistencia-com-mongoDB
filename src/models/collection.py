from datetime import date
from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional

class CollectionCreate(BaseModel):
    name: str = Field(
        ..., 
        title="Nome da Coleção",
        description="Nome único da coleção/set de cartas",
        min_length=2, 
        max_length=100,
        examples=["Coleção Alpha"]
    )
    release_date: date = Field(
        ...,
        title="Data de Lançamento",
        description="Data oficial de lançamento da coleção (AAAA-MM-DD)",
        examples=["2024-01-20"]
    )


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(
        None, 
        title="Nome da Coleção",
        description="Novo nome para a coleção",
        min_length=2, 
        max_length=100,
        examples=["Coleção Alpha Remastered"]
    )
    release_date: Optional[date] = Field(
        None,
        title="Data de Lançamento",
        description="Nova data de lançamento",
        examples=["2024-02-15"]
    )


class CollectionResponse(BaseModel):
    id: str = Field(..., title="ID", description="Identificador único da coleção no banco de dados")
    name: str = Field(..., title="Nome")
    release_date: date = Field(..., title="Lançamento")

    class Config:
        from_attributes = True


class Collection(Document):
    name : str
    release_date : date

    class Settings:
        name = "collections"