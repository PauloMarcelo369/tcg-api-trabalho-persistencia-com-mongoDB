import logging
from contextlib import asynccontextmanager
from fastapi_pagination import add_pagination

from fastapi import FastAPI

from src.core.database import close_db, init_db
from src.routes import collections 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
)
logger = logging.getLogger(__name__)



from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação com logging aprimorado e tratamento de erros."""
    try:
        logger.info("Iniciando aplicação...")
        await init_db()
        logger.info("Banco de dados inicializado com sucesso!")
        yield
    except Exception as e:
        logger.error(f"Erro durante o startup: {e}")
        raise
    finally:
        logger.info("Encerrando aplicação...")
        try:
            await close_db()
            logger.info("Conexão com banco de dados fechada com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão com o banco: {e}")


app = FastAPI(
    title="API de Filmes e Atores",
    description="API robusta para gerenciamento de decks, cards, coleções e usuaários com MongoDB",
    version="1.0.0",
    lifespan=lifespan,
)

add_pagination(app)

app.include_router(collections.router)


@app.get("/")
async def root():
    """Rota raiz da API"""
    return {
        "message": "Bem-vindo à API de Decks ",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }

@app.get("/health")
async def health_check():
    """Health check para verificar se a API está rodando"""
    return {"status": "healthy", "service": "API de Filmes"}