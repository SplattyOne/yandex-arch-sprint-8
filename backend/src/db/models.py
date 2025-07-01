from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class User(Base):
    """Модель пользователя в backend-е с ключевыми полями из keycloak"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    email_verified: Mapped[bool]
    name: Mapped[str]
    preferred_username: Mapped[str]
    given_name: Mapped[str]
    family_name: Mapped[str]


class Report(Base):
    """Модель отчетов без привязки к конкретным пользователям"""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
