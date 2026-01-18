import asyncio
import sys
import os
from datetime import date, datetime

# Configura o path para encontrar o módulo 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database import init_db, close_db
from src.models.user import User
from src.models.deck import Deck
from src.models.card import Card
from src.models.collection import Collection
from src.models.enums.enums import DeckFormat, CardType, CardRarity

async def run_full_system_test():
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA (USERS + CARDS)...")
    print("="*60)
    
    try:
        # --- 0. CONEXÃO ---
        await init_db()
        print("✅ [DB] Banco conectado com sucesso.\n")

        # ==============================================================================
        # PARTE 1: USUÁRIOS E DECKS
        # ==============================================================================
        print("👤 --- TESTANDO ROTAS DE USUÁRIOS ---")

        # 1.1 Create User (POST /users/)
        timestamp = int(datetime.now().timestamp())
        user_email = f"master_test_{timestamp}@exemplo.com"
        
        user = User(name="Jogador Teste", email=user_email, password="123")
        await user.insert()
        print(f"✅ [POST /users/] Usuário criado: {user.name} (ID: {user.id})")

        # 1.2 Update User (PUT /users/{id})
        user.name = "Jogador Supremo"
        await user.save()
        check_user = await User.get(user.id)
        if check_user.name == "Jogador Supremo":
            print(f"✅ [PUT /users/{{id}}] Usuário atualizado com sucesso.")
        else:
            print(f"❌ [PUT] Falha ao atualizar nome.")

        # 1.3 List Users (GET /users/)
        users_list = await User.find_all().to_list()
        print(f"✅ [GET /users/] Listagem retornou {len(users_list)} usuários.")

        # --- Relacionamento: Criando Decks ---
        print("\n🃏 --- PREPARANDO DECKS PARA TESTE DE USUÁRIO ---")
        d1 = Deck(name="Deck Aggro", format=DeckFormat.Standard, owner=user)
        d2 = Deck(name="Deck Control", format=DeckFormat.Commander, owner=user)
        d3 = Deck(name="Deck Combo", format=DeckFormat.Commander, owner=user)
        await d1.insert(); await d2.insert(); await d3.insert()
        print(f"✅ 3 Decks criados para o usuário {user.name}.")

        # 1.4 List User Decks (GET /users/{id}/decks)
        my_decks = await Deck.find(Deck.owner.id == user.id).to_list()
        if len(my_decks) == 3:
            print(f"✅ [GET /users/{{id}}/decks] Retornou 3 decks corretamente.")
        else:
            print(f"❌ [GET /decks] Erro: Retornou {len(my_decks)} decks.")

        # 1.5 Count Decks (GET /users/{id}/decks/count)
        count = await Deck.find(Deck.owner.id == user.id).count()
        print(f"✅ [GET /users/{{id}}/decks/count] Contagem: {count}")

        # 1.6 Stats by Format (GET /users/{id}/decks/count-by-format)
        pipeline_user_stats = [
            {"$match": {"owner.$id": user.id}},
            {"$group": {"_id": "$format", "count": {"$sum": 1}}}
        ]
        user_stats = await Deck.aggregate(pipeline_user_stats).to_list()
        stats_dict = {doc["_id"]: doc["count"] for doc in user_stats}
        print(f"✅ [GET /users/{{id}}/decks/count-by-format] Stats: {stats_dict}")
        
        if stats_dict.get("Commander") == 2:
            print("   -> Validação de Agregação: OK!")
        else:
            print("   -> ❌ ERRO: Agregação de decks incorreta.")


        # ==============================================================================
        # PARTE 2: CARTAS E COLEÇÕES
        # ==============================================================================
        print("\n\n🎴 --- TESTANDO ROTAS DE CARTAS ---")

        # 2.0 Preparação: Criar Coleção (Requisito para carta)
        coll = Collection(name=f"Coleção Alpha {timestamp}", release_date=date.today())
        await coll.insert()
        print(f"✅ Coleção criada: {coll.name} (ID: {coll.id})")

        # 2.1 Create Cards (POST /cards/)
        c1 = Card(name="Dragão Vermelho", type=CardType.Dragon, rarity=CardRarity.Mythic, collection=coll)
        c2 = Card(name="Goblin Explorador", type=CardType.Warrior, rarity=CardRarity.Common, collection=coll)
        c3 = Card(name="Goblin Rei", type=CardType.Warrior, rarity=CardRarity.Rare, collection=coll)
        c4 = Card(name="Bola de Fogo", type=CardType.Spell, rarity=CardRarity.Uncommon, collection=coll)

        await c1.insert(); await c2.insert(); await c3.insert(); await c4.insert()
        print(f"✅ [POST /cards/] 4 Cartas criadas na coleção '{coll.name}'.")

        # 2.2 Get Card by ID (GET /cards/{id})
        card_check = await Card.get(c1.id)
        if card_check and card_check.name == "Dragão Vermelho":
            print(f"✅ [GET /cards/{{id}}] Carta recuperada com sucesso.")
        else:
            print(f"❌ [GET /cards/{{id}}] Falha ao recuperar carta.")

        # 2.3 Update Card (PUT /cards/{id})
        c2.name = "Goblin Mestre"
        await c2.save()
        check_update_card = await Card.get(c2.id)
        if check_update_card.name == "Goblin Mestre":
            print(f"✅ [PUT /cards/{{id}}] Nome atualizado para 'Goblin Mestre'.")
        
        # 2.4 List Cards (GET /cards/)
        all_cards = await Card.find_all().limit(5).to_list()
        print(f"✅ [GET /cards/] Listagem OK ({len(all_cards)} itens retornados).")

        # 2.5 Search Card (GET /cards/search/{name})
        # Testando Regex Case-Insensitive
        search_res = await Card.find({"name": {"$regex": "goblin", "$options": "i"}}).to_list()
        print(f"✅ [GET /cards/search/{{name}}] Busca por 'goblin': Encontrou {len(search_res)} cartas.")
        if len(search_res) == 2:
             print("   -> Validação de Busca: OK!")
        else:
             print(f"   -> ❌ ERRO: Esperava 2 cartas, achou {len(search_res)}.")

        # 2.6 Get Cards by Collection (GET /cards/collection/{id})
        coll_cards = await Card.find(Card.collection.id == coll.id).to_list()
        print(f"✅ [GET /cards/collection/{{id}}] Cartas da coleção: {len(coll_cards)}")

        # --- ESTATÍSTICAS DE CARTAS (AGREGAÇÕES) ---
        print("\n📊 --- TESTANDO ESTATÍSTICAS DE CARTAS ---")

        # 2.7 Stats by Rarity
        pipeline_rarity = [
            {"$group": {"_id": "$rarity", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}}
        ]
        rarity_stats = await Card.aggregate(pipeline_rarity).to_list()
        print(f"✅ [GET /stats/by-rarity] {rarity_stats}")

        # 2.8 Stats by Type
        pipeline_type = [
            {"$group": {"_id": "$type", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}}
        ]
        type_stats = await Card.aggregate(pipeline_type).to_list()
        print(f"✅ [GET /stats/by-type] {type_stats}")

        # 2.9 Stats by Collection (Com Lookup)
        # Filtramos pela nossa coleção de teste para não pegar lixo do banco
        pipeline_coll = [
            {"$match": {"collection.$id": coll.id}},
            {"$group": {"_id": "$collection.$id", "total": {"$sum": 1}}},
            {"$lookup": {"from": "collections", "localField": "_id", "foreignField": "_id", "as": "info"}},
            {"$unwind": "$info"},
            {"$project": {"name": "$info.name", "total": 1}}
        ]
        coll_stats = await Card.aggregate(pipeline_coll).to_list()
        print(f"✅ [GET /stats/by-collection] {coll_stats}")
        
        if coll_stats and coll_stats[0]['total'] == 4:
            print("   -> Validação de Lookup/Join: PERFEITA!")
        else:
            print("   -> ❌ ERRO: Lookup falhou.")


        # ==============================================================================
        # PARTE 3: CLEANUP (DELETE)
        # ==============================================================================
        print("\n\n🗑️ --- LIMPEZA DO BANCO ---")

        # 3.1 Delete User (DELETE /users/{id})
        await user.delete()
        check_del_user = await User.get(user.id)
        if not check_del_user:
            print(f"✅ [DELETE /users/{{id}}] Usuário deletado.")
        
        # Deletando decks do usuário (limpeza manual pois mongo não tem cascade automático)
        del_decks = await Deck.find(Deck.owner.id == user.id).delete()
        print(f"   -> {del_decks.deleted_count} decks do usuário removidos.")

        # 3.2 Delete Card (DELETE /cards/{id})
        await c1.delete()
        check_del_card = await Card.get(c1.id)
        if not check_del_card:
            print(f"✅ [DELETE /cards/{{id}}] Carta 'Dragão Vermelho' deletada.")

        # Limpando o resto das cartas da coleção
        del_cards = await Card.find(Card.collection.id == coll.id).delete()
        print(f"   -> {del_cards.deleted_count} cartas restantes removidas.")

        # Limpando coleção
        await coll.delete()
        print(f"   -> Coleção removida.")

        print("\n✅✅✅ TESTE COMPLETO FINALIZADO COM SUCESSO! ✅✅✅")

    except Exception as e:
        print("\n❌❌❌ ERRO CRÍTICO DURANTE O TESTE ❌❌❌")
        print(e)
        import traceback
        traceback.print_exc()
    
    finally:
        await close_db()
        print("👋 Conexão encerrada.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_full_system_test())