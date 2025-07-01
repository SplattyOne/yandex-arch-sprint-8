from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import AddUser
from auth.dependencies import get_keycloak_client, check_administrator, check_prothetic_user
from auth.keycloak_client import KeycloakClient
from settings.config import settings
from db.dao import ReportsDAO, UsersDAO
from db.dependencies import (
    get_session_with_commit,
    get_session_without_commit,
)


router = APIRouter(prefix="/api", tags=["API"])


@router.get("/login/callback", include_in_schema=False)
async def login_callback(
    code: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    session: AsyncSession = Depends(get_session_with_commit),
    keycloak: KeycloakClient = Depends(get_keycloak_client),
) -> RedirectResponse:
    """
    Ванильный login без использования библиотеки.
    Обрабатывает callback после авторизации в Keycloak.
    Получает токен, информацию о пользователе, сохраняет пользователя в БД (если нужно)
    и устанавливает cookie с токенами. Обрабатывает ошибки от Keycloak.
    """
    if error:
        logger.error(f"Keycloak error: {error}, description: {error_description}")
        raise HTTPException(status_code=401, detail="Authorization code is required")

    if not code:
        raise HTTPException(status_code=401, detail="Authorization code is required")

    try:
        # Получение токенов от Keycloak
        token_data = await keycloak.get_tokens(code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        id_token = token_data.get("id_token")

        if not access_token:
            raise HTTPException(status_code=401, detail="Токен доступа не найден")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token не найден")
        if not id_token:
            raise HTTPException(status_code=401, detail="ID token не найден")

        # Получение информации о пользователе
        user_info = await keycloak.get_user_info(access_token)
        user_id = user_info.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="ID пользователя не найден")

        # Проверка существования пользователя, создание нового при необходимости
        users_dao = UsersDAO(session)
        user = await users_dao.find_one_or_none_by_id(user_id)
        if not user and isinstance(user_info, dict):
            user_info["id"] = user_info.pop("sub")
            await users_dao.add(AddUser(**user_info))

        # Установка cookie с токенами и редирект
        response = RedirectResponse(url="/protected")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
            max_age=token_data.get("expires_in", 3600),
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
            max_age=token_data.get("refresh_expires_in", 2592000),
        )
        response.set_cookie(
            key="id_token",
            value=id_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
            max_age=token_data.get("expires_in", 3600),
        )
        logger.info(f"User {user_id} logged in successfully")
        return response

    except Exception as e:
        logger.error(f"Ошибка обработки callback'а логина: {str(e)}")
        raise HTTPException(status_code=401, detail="Ошибка авторизации")


@router.get("/logout", include_in_schema=False)
async def logout(request: Request):
    """
    Ванильный logout без использования библиотеки.
    """
    id_token = request.cookies.get("id_token")
    params = {
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "post_logout_redirect_uri": settings.BASE_URL,
    }
    if id_token:
        params["id_token_hint"] = id_token

    keycloak_logout_url = f"{settings.logout_url}?{urlencode(params)}"
    response = RedirectResponse(url=keycloak_logout_url)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    response.delete_cookie(
        key="id_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/reports")
async def get_reports(
    current_user: dict = Depends(check_prothetic_user),
    session: AsyncSession = Depends(get_session_without_commit),
):
    """
    Возвращает все отчеты.
    check_prothetic_user - проверяет валидность access_token пользователя и проверяет роль пользователя протеза
    """
    reports_dao = ReportsDAO(session)
    reports = await reports_dao.find_all(None)
    return {"status": "ok", "reports": reports}


@router.get("/users")
async def get_users(
    current_user: dict = Depends(check_administrator),
    session: AsyncSession = Depends(get_session_without_commit),
):
    """
    Возвращает всех пользователей.
    check_administrator - проверяет валидность access_token пользователя и проверяет роль администратора
    """
    users_dao = UsersDAO(session)
    users = await users_dao.find_all(None)
    return {"status": "ok", "users": users}
