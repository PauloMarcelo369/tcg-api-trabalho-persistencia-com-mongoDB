from typing import Optional, List
from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel
from src.models.enums.enums import CardType, CardRarity
from src.models.collection import Collection

class Card(Document):
    name: str
    type: CardType
    rarity: CardRarity
    text: Optional[str] = None
    collection: Link[Collection]

    class Settings:
        name = "cards"

class CardCreate(BaseModel):
    name: str
    type: CardType
    rarity: CardRarity
    text: Optional[str] = None
    collection_id: PydanticObjectId  

class CardUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[CardType] = None
    rarity: Optional[CardRarity] = None
    text: Optional[str] = None
    collection_id: Optional[PydanticObjectId] = None 

class CardRead(BaseModel):
    id: PydanticObjectId
    name: str
    type: CardType
    rarity: CardRarity
    text: Optional[str] = None
    collection_id: Optional[PydanticObjectId] = None
    
    def __init__(self, **data):
        if 'collection' in data and data['collection']:
            link = data.pop('collection')
            data['collection_id'] = link.id if hasattr(link, 'id') else link.ref.id
        super().__init__(**data)