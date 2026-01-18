from datetime import datetime
from beanie import Document, Link
from typing import List
from src.models.card import Card
from src.models.enums.enums import DeckFormat
from src.models.user import User

class Deck(Document):
    name: str
    format: DeckFormat
    created_at: datetime = datetime.now()
    owner: Link["User"] 
    cards: List[Link[Card]] = []

    class Settings:
        name = "decks"
