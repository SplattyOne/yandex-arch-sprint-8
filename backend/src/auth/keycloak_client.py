from fastapi import HTTPException
from keycloak import KeycloakOpenID, KeycloakError
from loguru import logger

from settings.config import settings


class KeycloakClient:
    def __init__(self, client: KeycloakOpenID | None = None):
        self.client = client or KeycloakOpenID(
            server_url=settings.KEYCLOAK_BASE_URL,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            realm_name=settings.KEYCLOAK_REALM,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET
        )

    async def get_tokens(self, code: str) -> dict:
        """Обмен authorization code на токены"""
        try:
            access_token = await self.client.a_token(
                grant_type='authorization_code',
                code=code,
                redirect_uri=settings.redirect_uri
            )
            logger.info(f'Success in get_tokens: {access_token}')
            return access_token
        except KeycloakError as e:
            logger.error(f'Token exchange failed in get_user_info: {e}')
            raise HTTPException(
                status_code=500, detail=f"Token exchange failed: {str(e)}"
            )

    async def get_user_info(self, token: str) -> dict:
        """Получить информацию о пользователе по access_token"""
        try:
            decoded_token = await self.client.a_decode_token(token, validate=False)
            logger.info(f"Decoded token in get_user_info: {decoded_token}")
            # userinfo = await self.client.a_userinfo(token)
            # logger.info(f'User in get_user_info: {userinfo}')
            return decoded_token
        except KeycloakError as e:
            logger.error(f'Get user failed in get_user_info: {e}')
            raise HTTPException(
                status_code=500, detail=f"Get user failed in get_user_info: {str(e)}"
            )

    async def logout(self, refresh_token: str) -> None:
        try:
            await self.client.a_logout(refresh_token)
        except KeycloakError as e:
            logger.error(f'Logout failed in get_user_info: {e}')
            raise HTTPException(
                status_code=500, detail=f"Logout failed: {str(e)}"
            )

    async def refresh(self, refresh_token: str) -> dict:
        try:
            return await self.client.a_refresh_token(refresh_token)
        except KeycloakError as e:
            logger.error(f'Refresh token failed: {e}')
            raise HTTPException(
                status_code=500, detail=f"Refresh token failed: {str(e)}"
            )
