from beanie import Document, Link
from typing import Optional
from enums.enums import CardRarity, CardType
from collection import Collection

class Card(Document):
    name: str
    type: CardType
    rarity: CardRarity
    text: Optional[str] = None
    collection: Link[Collection]

    class Settings:
        name = "cards"
