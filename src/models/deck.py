from datetime import datetime
from beanie import Document, Link
from typing import List
from pydantic import BaseModel, Field
from src.models.card import Card
from src.models.enums.enums import DeckFormat
from src.models.user import User


class AddCardsRequest(BaseModel):
    card_ids: List[str]

class Deck(Document):
    name: str = Field(..., min_length=2, max_length=100)
    format: DeckFormat
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner: Link["User"] 
    cards: List[Link[Card]] = []

    class Settings:
        name = "decks"

class DeckCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    format: DeckFormat
    owner_id: str


class DeckUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    format: DeckFormat | None
    card_ids: List[str] | None

class DeckResponse(BaseModel):
    id: str
    name: str
    format: DeckFormat
    created_at: datetime
    owner: User        
    cards_ids: List[str]

    class Config:
        from_attributes = True
