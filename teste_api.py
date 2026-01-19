import sys
import os
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
# Certifique-se de que o 'httpx' está instalado: pip install httpx

# Importa a instância da aplicação FastAPI do seu main.py
from main import app 

def run_tests():
    print("🚀 Iniciando Testes Automatizados da API TCG...")
    
    # Gera um sufixo único para esta execução (ex: _17123456)
    unique_id = int(datetime.now().timestamp())
    
    with TestClient(app) as client:
        
        user_id = None
        collection_id = None
        card_id_1 = None
        card_id_2 = None
        deck_id = None

        # ==========================================
        # 1. TESTES DE USUÁRIOS (Users)
        # ==========================================
        print("\n👤 --- Testando Rotas de Usuários ---")

        # 1.1 Criar Usuário
        user_payload = {
            "name": f"Duelista Teste {unique_id}",
            "email": f"teste_{unique_id}@email.com", 
            "password": "senhaForte123!"
        }
        response = client.post("/users/", json=user_payload)
        if response.status_code != 201:
            print(f"❌ Falha ao criar usuário: {response.text}")
            return
        
        user_data = response.json()
        user_id = user_data["id"]
        print(f"✅ POST /users/ - Usuário criado (ID: {user_id})")

        # 1.2 Buscar Usuário por ID
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        print(f"✅ GET /users/{{id}} - Usuário encontrado")

        # 1.3 Listar Usuários
        response = client.get("/users/")
        assert response.status_code == 200
        assert len(response.json()["items"]) > 0
        print(f"✅ GET /users/ - Listagem de usuários OK")

        # 1.4 Atualizar Usuário
        update_payload = {"name": f"Duelista Supremo {unique_id}"}
        response = client.put(f"/users/{user_id}", json=update_payload)
        assert response.status_code == 200
        assert response.json()["name"] == update_payload["name"]
        print(f"✅ PUT /users/{{id}} - Usuário atualizado")

        # ==========================================
        # 2. TESTES DE COLEÇÕES (Collections)
        # ==========================================
        print("\n📚 --- Testando Rotas de Coleções ---")

        # 2.1 Criar Coleção
        collection_payload = {
            "name": f"Coleção Alpha {unique_id}",
            "release_date": date.today().isoformat()
        }
        response = client.post("/collections/", json=collection_payload)
        if response.status_code != 201:
            print(f"❌ Falha ao criar coleção: {response.text}")
            return

        collection_data = response.json()
        collection_id = collection_data["id"]
        print(f"✅ POST /collections/ - Coleção criada (ID: {collection_id})")

        # 2.2 Buscar Coleção por ID
        response = client.get(f"/collections/{collection_id}")
        assert response.status_code == 200
        print(f"✅ GET /collections/{{id}} - Coleção encontrada")

        # 2.3 Listar Coleções
        response = client.get("/collections/")
        assert response.status_code == 200
        print(f"✅ GET /collections/ - Listagem OK")

        # 2.4 Atualizar Coleção
        update_col_payload = {"name": f"Coleção Beta {unique_id}"}
        response = client.put(f"/collections/{collection_id}", json=update_col_payload)
        assert response.status_code == 200
        assert response.json()["name"] == update_col_payload["name"]
        print(f"✅ PUT /collections/{{id}} - Coleção atualizada")

        # 2.5 Buscar (Search) Coleções
        # Usamos "Beta" na busca pois atualizamos o nome para "Coleção Beta ..."
        response = client.get("/collections/search?query=Beta")
        assert response.status_code == 200
        assert len(response.json()["items"]) > 0
        print(f"✅ GET /collections/search - Busca OK")

        # 2.6 Contar Coleções
        response = client.get("/collections/count")
        assert response.status_code == 200
        print(f"✅ GET /collections/count - Contagem: {response.json()['total']}")

        # 2.7 Filtrar por Ano
        current_year = date.today().year
        response = client.get(f"/collections/filter/by-year?year={current_year}")
        assert response.status_code == 200
        print(f"✅ GET /collections/filter/by-year - Filtro OK")

        # 2.8 Stats by Year
        response = client.get("/collections/stats/by-year")
        assert response.status_code == 200
        print(f"✅ GET /collections/stats/by-year - Stats OK")

        # ==========================================
        # 3. TESTES DE CARTAS (Cards)
        # ==========================================
        print("\n🃏 --- Testando Rotas de Cartas ---")

        # 3.1 Criar Carta 1 (Nome Único)
        card1_payload = {
            "name": f"Dragão {unique_id}",
            "type": "Dragon",
            "rarity": "Rare",
            "text": "Destrói tudo.",
            "collection_id": collection_id
        }
        response = client.post("/cards/", json=card1_payload)
        if response.status_code != 201:
            print(f"❌ Erro criar carta 1: {response.text}")
            return
        card_id_1 = response.json()["id"]
        print(f"✅ POST /cards/ - Carta 1 criada (ID: {card_id_1})")

        # 3.2 Criar Carta 2 (Nome Único)
        card2_payload = {
            "name": f"Mago {unique_id}",
            "type": "Magician",
            "rarity": "Common",
            "text": "Magia arcana.",
            "collection_id": collection_id
        }
        response = client.post("/cards/", json=card2_payload)
        assert response.status_code == 201
        card_id_2 = response.json()["id"]
        print(f"✅ POST /cards/ - Carta 2 criada (ID: {card_id_2})")

        # 3.3 Buscar Carta por ID
        response = client.get(f"/cards/{card_id_1}")
        assert response.status_code == 200
        print(f"✅ GET /cards/{{id}} - Carta encontrada")

        # 3.4 Listar Cartas
        response = client.get("/cards/")
        assert response.status_code == 200
        print(f"✅ GET /cards/ - Listagem OK")

        # 3.5 Atualizar Carta
        update_card_payload = {"rarity": "Mythic"}
        response = client.put(f"/cards/{card_id_1}", json=update_card_payload)
        assert response.status_code == 200
        assert response.json()["rarity"] == "Mythic"
        print(f"✅ PUT /cards/{{id}} - Carta atualizada")

        # 3.6 Buscar Cartas (Search)
        response = client.get(f"/cards/search?query=Dragão")
        assert response.status_code == 200
        assert len(response.json()["items"]) > 0
        print(f"✅ GET /cards/search - Busca OK")

        # 3.7 Stats by Rarity
        response = client.get("/cards/stats/by-rarity")
        assert response.status_code == 200
        print(f"✅ GET /cards/stats/by-rarity - Stats OK")

        # 3.8 Stats by Type
        response = client.get("/cards/stats/by-type")
        assert response.status_code == 200
        print(f"✅ GET /cards/stats/by-type - Stats OK")

        # 3.9 Obter cartas de uma coleção
        response = client.get(f"/collections/{collection_id}/cards")
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 2
        print(f"✅ GET /collections/{{id}}/cards - Cartas da coleção recuperadas")

        # 3.10 Stats Collections with Cards
        response = client.get("/collections/stats/with-cards")
        assert response.status_code == 200
        print(f"✅ GET /collections/stats/with-cards - Stats OK")

        # ==========================================
        # 4. TESTES DE DECKS (Decks)
        # ==========================================
        print("\n🎴 --- Testando Rotas de Decks ---")

        # 4.1 Criar Deck (Nome Único)
        deck_payload = {
            "name": f"Deck Campeão {unique_id}",
            "format": "Standard",
            "owner_id": user_id
        }
        response = client.post("/decks/", json=deck_payload)
        if response.status_code != 201:
            print(f"❌ Erro criar deck: {response.text}")
            return
        deck_id = response.json()["id"]
        print(f"✅ POST /decks/ - Deck criado (ID: {deck_id})")

        # 4.2 Adicionar Cartas ao Deck
        add_cards_payload = {"card_ids": [card_id_1, card_id_2]}
        response = client.post(f"/decks/{deck_id}/add_cards", json=add_cards_payload)
        assert response.status_code == 200
        assert len(response.json()["cards_ids"]) == 2
        print(f"✅ POST /decks/{{id}}/add_cards - Cartas adicionadas")

        # 4.3 Remover Carta do Deck
        response = client.post(f"/decks/{deck_id}/remove_card/{card_id_2}")
        assert response.status_code == 200
        assert len(response.json()["cards_ids"]) == 1
        print(f"✅ POST /decks/{{id}}/remove_card/{{card_id}} - Carta removida")

        # 4.4 Listar Decks
        response = client.get("/decks/")
        assert response.status_code == 200
        print(f"✅ GET /decks/ - Listagem OK")

        # 4.5 Buscar Deck por Search
        response = client.get("/decks/search?query=Campeão")
        assert response.status_code == 200
        assert len(response.json()["items"]) > 0
        print(f"✅ GET /decks/search - Busca OK")

        # 4.6 Filtrar por Formato
        response = client.get("/decks/by-format/Standard")
        assert response.status_code == 200
        print(f"✅ GET /decks/by-format/{{format}} - Filtro OK")

        # 4.7 Filtrar por Data
        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = (datetime.now() + timedelta(days=1)).isoformat()
        response = client.get(f"/decks/by-date?start={start_date}&end={end_date}")
        assert response.status_code == 200
        print(f"✅ GET /decks/by-date - Filtro por data OK")

        # 4.8 Get Deck Cards
        response = client.get(f"/decks/{deck_id}/cards")
        assert response.status_code == 200
        print(f"✅ GET /decks/{{id}}/cards - Cartas do deck recuperadas")

        # 4.9 Update Deck
        update_deck_payload = {"name": f"Deck Lendário {unique_id}"}
        response = client.put(f"/decks/{deck_id}", json=update_deck_payload)
        assert response.status_code == 200
        assert response.json()["name"] == update_deck_payload["name"]
        print(f"✅ PUT /decks/{{id}} - Deck atualizado")

        # 4.10 Count Decks
        response = client.get("/decks/count")
        assert response.status_code == 200
        print(f"✅ GET /decks/count - Contagem OK")

        # 4.11 Stats by Format
        response = client.get("/decks/stats/by-format")
        assert response.status_code == 200
        print(f"✅ GET /decks/stats/by-format - Stats OK")

        # ==========================================
        # 5. LIMPEZA (Cleanup)
        # ==========================================
        print("\n🗑️  --- Testando Remoção (Cleanup) ---")

        # 5.1 Deletar Carta
        response = client.delete(f"/cards/{card_id_1}")
        assert response.status_code == 204
        print(f"✅ DELETE /cards/{{id}} - Carta deletada")

        # 5.2 Deletar Coleção
        response = client.delete(f"/collections/{collection_id}")
        assert response.status_code == 200
        print(f"✅ DELETE /collections/{{id}} - Coleção deletada")

        # 5.3 Deletar Usuário
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 204
        print(f"✅ DELETE /users/{{id}} - Usuário deletado")

        print("\n✨ Todos os testes foram concluídos com sucesso! ✨")

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU (Assertion): {e}")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")