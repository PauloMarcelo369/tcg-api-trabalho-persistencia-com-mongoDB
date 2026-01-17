from datetime import datetime
from beanie import Document, Link
from typing import List
from card import Card
from enums.enums import DeckFormat
from user import User

class Deck(Document):
    name: str
    format: DeckFormat
    created_at: datetime = datetime.now()
    owner: Link["User"] 
    cards: List[Link[Card]] = []

    class Settings:
        name = "decks"
