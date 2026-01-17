from datetime import date
from beanie import Document


class Collection(Document):
    name : str
    release_date : date

    class Settings:
        name = "collections"