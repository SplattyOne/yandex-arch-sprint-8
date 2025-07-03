import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    KEYCLOAK_BASE_URL: str = Field(default='', alias='KEYCLOAK_BASE_URL')
    BASE_URL: str = Field(default='', alias='BASE_URL')
    KEYCLOAK_REALM: str = Field(default='', alias='KEYCLOAK_REALM')
    KEYCLOAK_CLIENT_ID: str = Field(default='', alias='KEYCLOAK_CLIENT_ID')
    KEYCLOAK_CLIENT_SECRET: str = Field(default='', alias='KEYCLOAK_CLIENT_SECRET')
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    KEYCLOAK_ADMIN_ROLE: str = Field(default='', alias='KEYCLOAK_ADMIN_ROLE')
    KEYCLOAK_PROTHETIC_USER_ROLE: str = Field(default='', alias='KEYCLOAK_PROTHETIC_USER_ROLE')

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.BASE_DIR}/backend-data/db.sqlite3"

    @property
    def token_url(self) -> str:
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/token"

    @property
    def auth_url(self) -> str:
        return (
            f"{self.KEYCLOAK_BASE_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/auth"
        )

    @property
    def logout_url(self) -> str:
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/logout"

    @property
    def userinfo_url(self) -> str:
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/userinfo"

    @property
    def redirect_uri(self) -> str:
        return f"{self.BASE_URL}/api/login/callback"

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")


settings = Settings()
