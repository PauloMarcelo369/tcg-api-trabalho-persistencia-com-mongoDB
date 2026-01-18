from datetime import datetime
from beanie import Document
from typing import List
from pydantic import Field

class User(Document):
    name: str
    email: str
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
