from datetime import datetime
from beanie import Document, Link
from typing import List, Optional
from pydantic import BaseModel, Field
from src.models.card import Card
from src.models.enums.enums import DeckFormat
from src.models.user import User


class AddCardsRequest(BaseModel):
    card_ids: List[str] = Field(
        ...,
        description="Lista de IDs das cartas a adicionar",
        examples=[["64f1b2b2e1b2b2e1b2b2e1b2"]]
    )

class Deck(Document):
    name: str = Field(..., min_length=2, max_length=100)
    format: DeckFormat
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner: Link["User"] 
    cards: List[Link[Card]] = []

    class Settings:
        name = "decks"

class DeckCreate(BaseModel):
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        title="Nome do Deck",
        examples=["Dragon Stompy"]
    )
    format: DeckFormat = Field(
        ..., 
        title="Formato",
        examples=[DeckFormat.Standard]
    )
    owner_id: str = Field(
        ..., 
        title="ID do Dono",
        description="ID do usuário proprietário do deck",
        examples=["65a9f... (coloque um ID real de usuario aqui)"]
    )


class DeckUpdate(BaseModel):
    name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=100,
        title="Nome",
        examples=["Dragon Stompy v2"]
    )
    format: Optional[DeckFormat] = Field(None, title="Formato")
    card_ids: Optional[List[str]] = Field(
        None, 
        title="Lista de Cartas",
        description="Substitui todas as cartas do deck por esta lista nova"
    )

class DeckResponse(BaseModel):
    id: str
    name: str
    format: DeckFormat
    created_at: datetime
    owner: User        
    cards_ids: List[str]

    class Config:
        from_attributes = True