from typing import Generic, TypeVar

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import Base


T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: type[T]

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("Модель должна быть указана в дочернем классе")

    async def find_one_or_none_by_id(self, data_id: int):
        # Найти запись по ID
        try:
            query = select(self.model).filter_by(id=data_id)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с ID {data_id} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise

    async def find_one_or_none(self, filters: BaseModel):
        # Найти одну запись по фильтрам
        filter_dict = filters.model_dump(exclude_unset=True)
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            logger.info(f"Запись {self.model.__name__} с фильтрами {filter_dict} "
                        f"{'найдена' if record else 'не найдена'}.")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с фильтрами {filter_dict}: {e}")
            raise

    async def find_all(self, filters: BaseModel | None):
        if filters:
            filter_dict = filters.model_dump(exclude_unset=True)
        else:
            filter_dict = {}
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            records = result.scalars().all()
            logger.info(f"Записи {self.model.__name__} с фильтрами {filter_dict} "
                        f"{'найдены' if records else 'не найдены'}.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записей с фильтрами {filter_dict}: {e}")
            raise

    async def add(self, values: BaseModel):
        # Добавить одну запись
        values_dict = values.model_dump(exclude_unset=True)
        new_instance = self.model(**values_dict)
        self._session.add(new_instance)
        try:
            await self._session.flush()
            logger.info(f"Запись {self.model.__name__} с параметрами {values_dict} добавлена.")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении записи с параметрами {values_dict}: {e}")
            await self._session.rollback()
            raise e
        return new_instance

    async def update_one_by_id(self, data_id: int, values: BaseModel):
        # Обновить запись по ID
        values_dict = values.model_dump(exclude_unset=True)
        try:
            record = await self._session.get(self.model, data_id)
            for key, value in values_dict.items():
                setattr(record, key, value)
            await self._session.flush()
            logger.info(f"Запись {self.model.__name__} с id {data_id} и параметрами {values_dict} обновлена.")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении записи с id {data_id} и параметрами {values_dict}: {e}")
            raise e

    async def delete_one_by_id(self, data_id: int):
        # Удалить запись по ID
        try:
            data = await self._session.get(self.model, data_id)
            if data:
                await self._session.delete(data)
                await self._session.flush()
            logger.info(f"Запись {self.model.__name__} с id {data_id} удалена.")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении записи с id {data_id}: {e}")
            raise
