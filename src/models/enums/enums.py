from enum import Enum

class CardType(str, Enum):
    Dragon = "Dragon"
    Warrior = "Warrior"
    Magician = "Magician"
    Dinosaur = "Dinosaur"
    Spell = "Spell"
    Mage = "Mage"

class CardRarity(str, Enum):
    Common = "Common"
    Uncommon = "Uncommon"
    Rare = "Rare"
    Mythic = "Mythic"

class DeckFormat(str, Enum):
    Standard = "Standard"
    Modern = "Modern"
    Commander = "Commander"
    Pauper = "Pauper"
