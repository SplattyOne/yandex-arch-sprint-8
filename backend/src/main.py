import asyncio
from contextlib import asynccontextmanager
import sys

from alembic.config import Config
from alembic import command
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from keycloak import KeycloakOpenID
from loguru import logger

from settings.config import settings
from auth.keycloak_client import KeycloakClient

from api.router import router as api_router

# Очистка стандартных хендлеров
logger.remove()

# Настройка логгирования в stdout с debug-информацией
logger.add(
    sys.stdout,
    level="DEBUG",
    backtrace=True,
    diagnose=True,  # Показывает подробности при исключениях
    enqueue=True,   # Thread-safe логгирование
)


async def run_migrations() -> None:
    # Выполняет миграции в БД
    alembic_cfg = Config("alembic.ini")
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    #  Создаем и сохраняем shared клиент
    keycloak_client = KeycloakOpenID(
        server_url=settings.KEYCLOAK_BASE_URL,
        client_id=settings.KEYCLOAK_CLIENT_ID,
        realm_name=settings.KEYCLOAK_REALM,
        client_secret_key=settings.KEYCLOAK_CLIENT_SECRET
    )
    app.state.keycloak_client = KeycloakClient(keycloak_client)

    # Миграции БД
    await run_migrations()

    #  Подключаем роутеры и статику
    app.include_router(api_router)

    yield

    #  Закрываем клиент
    await keycloak_client.connection.aclose()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    """Автоматический перехват ошибки 401 из методов router и перенаправление на страницу входв keycloak"""
    if exc.status_code == 401:
        return RedirectResponse(
            f"{settings.auth_url}"
            f"?client_id={settings.KEYCLOAK_CLIENT_ID}"
            f"&response_type=code"
            f"&scope=openid"
            f"&redirect_uri={settings.redirect_uri}"
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
