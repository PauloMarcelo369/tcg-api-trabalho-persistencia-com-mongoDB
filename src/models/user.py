from datetime import datetime
from beanie import Document
from typing import List
from pydantic import BaseModel
from typing import Optional
from beanie import PydanticObjectId

class User(Document):
    name: str
    email: str
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserRead(BaseModel):
    id: PydanticObjectId
    name: str
    email: str
    created_at: datetime