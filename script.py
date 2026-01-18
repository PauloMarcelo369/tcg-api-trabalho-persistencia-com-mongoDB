import asyncio
from datetime import date
import random

from src.core.database import init_db, close_db
from src.models.user import User
from src.models.collection import Collection
from src.models.card import Card
from src.models.deck import Deck
from src.models.enums.enums import CardType, CardRarity, DeckFormat


async def seed_database():
    print("🌱 Populando MongoDB com dados reais...")

    # Limpa coleções
    await Deck.delete_all()
    await Card.delete_all()
    await Collection.delete_all()
    await User.delete_all()

    # ----------------------
    # USERS (10)
    # ----------------------
    users_data = [
        ("Paulo Marcelo", "paulo@email.com"),
        ("Lucas Andrade", "lucas@email.com"),
        ("Mariana Silva", "mariana@email.com"),
        ("Rafael Costa", "rafael@email.com"),
        ("Ana Beatriz", "ana@email.com"),
        ("Pedro Henrique", "pedro@email.com"),
        ("Juliana Rocha", "juliana@email.com"),
        ("Gabriel Souza", "gabriel@email.com"),
        ("Camila Torres", "camila@email.com"),
        ("Felipe Martins", "felipe@email.com"),
    ]

    users = []
    for name, email in users_data:
        user = User(name=name, email=email, password="123456")
        await user.insert()
        users.append(user)

    # ----------------------
    # COLLECTIONS (10)
    # ----------------------
    collections_data = [
        ("Base Origins", date(2018, 3, 15)),
        ("Dark Eclipse", date(2019, 6, 10)),
        ("Ancient Legends", date(2020, 1, 20)),
        ("Crystal Storm", date(2020, 11, 5)),
        ("Shadow Reign", date(2021, 4, 12)),
        ("Flames of Destiny", date(2021, 9, 30)),
        ("Frozen Horizon", date(2022, 2, 18)),
        ("Mythic Dawn", date(2022, 8, 7)),
        ("Eternal Chaos", date(2023, 3, 22)),
        ("Celestial Wars", date(2024, 1, 10)),
    ]

    collections = []
    for name, release_date in collections_data:
        collection = Collection(name=name, release_date=release_date)
        await collection.insert()
        collections.append(collection)

    # ----------------------
    # CARDS (10)
    # ----------------------
    cards_data = [
        ("Dragão Azul Celestial", CardType.Dragon, CardRarity.Rare),
        ("Mago Sombrio Arcano", CardType.Magician, CardRarity.Rare),
        ("Guerreiro da Aurora", CardType.Warrior, CardRarity.Common),
        ("Feiticeira Carmesim", CardType.Magician, CardRarity.Rare),
        ("Titã de Pedra Ancestral", CardType.Dinosaur, CardRarity.Common),
        ("Espírito do Abismo", CardType.Dragon, CardRarity.Common),
        ("Fênix das Chamas Eternas", CardType.Mage, CardRarity.Mythic),
        ("Guardião do Norte", CardType.Dinosaur, CardRarity.Common),
        ("Serpente do Caos", CardType.Dragon, CardRarity.Rare),
        ("Anjo da Luz Final", CardType.Warrior, CardRarity.Mythic),
    ]

    cards = []
    for i, (name, ctype, rarity) in enumerate(cards_data):
        card = Card(
            name=name,
            type=ctype,
            rarity=rarity,
            text=f"{name} é uma carta poderosa com habilidades únicas.",
            collection=collections[i % len(collections)],
        )
        await card.insert()
        cards.append(card)

    # ----------------------
    # DECKS (10)
    # ----------------------
    decks_data = [
        "Ascensão Celestial",
        "Sombras do Abismo",
        "Chamas Eternas",
        "Guardiões Antigos",
        "Caos Primordial",
        "Aurora Sagrada",
        "Reinado das Trevas",
        "Fúria Elemental",
        "Luz contra Escuridão",
        "Destino Final",
    ]

    for i, deck_name in enumerate(decks_data):
        deck = Deck(
            name=deck_name,
            format=random.choice(list(DeckFormat)),
            owner=users[i % len(users)],
            cards=[
                cards[i % len(cards)],
                cards[(i + 1) % len(cards)],
                cards[(i + 2) % len(cards)],
            ],
        )
        await deck.insert()

    print("✅ Banco populado com dados reais!")
    print("→ 10 users")
    print("→ 10 collections")
    print("→ 10 cards")
    print("→ 10 decks")


async def main():
    await init_db()
    try:
        await seed_database()
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
