from datetime import datetime
from beanie import Document
from typing import List

class User(Document):
    name: str
    email: str
    password: str
    created_at: datetime = datetime.now()

    class Settings:
        name = "users"
