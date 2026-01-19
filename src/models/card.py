from typing import Optional, List
from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field
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

class RemoveCardsRequest(BaseModel):
    card_ids: List[str] = Field(
        ..., 
        description="Lista de IDs das cartas a serem removidas",
        examples=[["64f1b2b2e1b2b2e1b2b2e1b2"]]
    )

class CardCreate(BaseModel):
    name: str = Field(
        ..., 
        title="Nome da Carta",
        description="Nome único da carta no jogo",
        min_length=1,
        examples=["Black Lotus"]
    )
    type: CardType = Field(
        ..., 
        title="Tipo",
        description="Categoria da carta (Dragon, Spell, etc.)",
        examples=[CardType.Spell]
    )
    rarity: CardRarity = Field(
        ..., 
        title="Raridade",
        description="Nível de raridade da carta",
        examples=[CardRarity.Rare]
    )
    text: Optional[str] = Field(
        None, 
        title="Texto de Efeito",
        description="Descrição da habilidade ou flavor text da carta",
        examples=["Add three mana of any one color to your mana pool."]
    )
    collection_id: PydanticObjectId = Field(
        ..., 
        title="ID da Coleção",
        description="ID da coleção (set) à qual esta carta pertence",
        examples=["64f1b2b2e1b2b2e1b2b2e1b2"]
    )

class CardUpdate(BaseModel):
    name: Optional[str] = Field(
        None, 
        title="Nome",
        description="Novo nome da carta",
        examples=["Black Lotus Alpha"]
    )
    type: Optional[CardType] = Field(
        None, 
        title="Tipo",
        examples=[CardType.Spell]
    )
    rarity: Optional[CardRarity] = Field(
        None, 
        title="Raridade",
        examples=[CardRarity.Mythic]
    )
    text: Optional[str] = Field(
        None, 
        title="Texto",
        description="Atualização do texto da carta"
    )
    collection_id: Optional[PydanticObjectId] = Field(
        None, 
        title="ID da Coleção",
        description="Mover a carta para outra coleção"
    )

class CardRead(BaseModel):
    id: PydanticObjectId = Field(..., title="ID da Carta")
    name: str = Field(..., title="Nome")
    type: CardType = Field(..., title="Tipo")
    rarity: CardRarity = Field(..., title="Raridade")
    text: Optional[str] = Field(None, title="Texto")
    collection_id: Optional[PydanticObjectId] = Field(None, title="ID da Coleção")
    
    def __init__(self, **data):
        if 'collection' in data and data['collection']:
            link = data.pop('collection')
            data['collection_id'] = link.id if hasattr(link, 'id') else link.ref.id
        super().__init__(**data)