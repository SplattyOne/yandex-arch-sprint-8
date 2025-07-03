from fastapi import Depends, HTTPException, Request
from auth.keycloak_client import KeycloakClient
from loguru import logger

from settings.config import settings


#  Получаем KeycloakClient из app.state
def get_keycloak_client(request: Request) -> KeycloakClient:
    return request.app.state.keycloak_client


# Получаем токен из cookie
async def get_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get("access_token")


# Получаем пользователя по токену
async def get_current_user(
    token: str = Depends(get_token_from_cookie),
    keycloak: KeycloakClient = Depends(get_keycloak_client),
) -> dict:
    if not token:
        logger.error('No access token in get_current_user')
        raise HTTPException(status_code=401, detail="Unauthorized: No access token")

    try:
        user_info = await keycloak.get_user_info(token)
        return user_info
    except HTTPException as e:
        logger.error(f'Invalid token in get_current_user: {e}')
        raise HTTPException(status_code=401, detail="Invalid token")


# Проверяем администратора
async def check_administrator(
    current_user: dict = Depends(get_current_user),
) -> dict:
    current_roles = current_user.get('realm_access', {}).get('roles', [])
    if settings.KEYCLOAK_ADMIN_ROLE not in current_roles:
        logger.error(f'Wrong user roles, not administrator user: {current_roles}')
        raise HTTPException(status_code=403, detail=f'Wrong user roles, not administrator user: {current_roles}')
    return current_user


# Проверяем пользователя протезом
async def check_prothetic_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    current_roles = current_user.get('realm_access', {}).get('roles', [])
    if settings.KEYCLOAK_PROTHETIC_USER_ROLE not in current_roles:
        logger.error(f'Wrong user roles, not prothetic user: {current_roles}')
        raise HTTPException(status_code=403, detail=f'Wrong user roles, not prothetic user: {current_roles}')
    return current_user
