from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from settings.config import settings


# Фабрика асинхронных сессий
engine = create_async_engine(url=settings.database_url)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс с часто используемыми полями created_dt и update_dt"""
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )
