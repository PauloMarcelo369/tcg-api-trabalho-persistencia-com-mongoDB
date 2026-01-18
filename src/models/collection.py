from datetime import date
from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional

class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    release_date: date


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    release_date: Optional[date]


class CollectionResponse(BaseModel):
    id: str
    name: str
    release_date: date

    class Config:
        from_attributes = True


class Collection(Document):
    name : str
    release_date : date

    class Settings:
        name = "collections"