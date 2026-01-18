from beanie import Document, Link
from typing import Optional
from src.models.enums.enums import CardType, CardRarity
from src.models.collection import Collection
from pydantic import BaseModel
from typing import List

class Card(Document):
    name: str
    type: CardType
    rarity: CardRarity
    text: Optional[str] = None
    collection: Link[Collection]

    class Settings:
        name = "cards"

class RemoveCardsRequest(BaseModel):
    card_ids: List[str]