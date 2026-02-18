from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from app.database import async_session_maker


class BaseDAO:
    model = None

    # Если фильтры не указаны, то будут возвращены все значения
    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(selectinload(cls.model.major))
                .filter_by(**filter_by)
            )
            result = await session.execute(query)
            return result.scalars().all()


    @classmethod
    async def find_one(cls, **filter_by):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(selectinload(cls.model.major))
                .filter_by(**filter_by)
            )
            result = await session.execute(query)
            return result.scalar_one()


    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(selectinload(cls.model.major))
                .filter_by(**filter_by)
            )
            result = await session.execute(query)
            return result.scalars().one_or_none()
        

    @classmethod
    async def add(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance


    @classmethod
    async def update(cls, filter_by: dict, **values):
        async with async_session_maker() as session:
            async with session.begin():
                stmt = (
                    sqlalchemy_update(cls.model)
                    .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                    .values(**values)
                    .returning(cls.model)
                )
                result = await session.execute(stmt)
                return result.scalars().one_or_none()

    
    @classmethod
    async def delete(cls, delete_all: bool = False, **filter_by):
        if not delete_all and not filter_by:
            raise ValueError("Необходимо указать хотя бы один параметр для удаления")

        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_delete(cls.model)
                    .filter_by(**filter_by)
                    .returning(cls.model)
                )
                result = await session.execute(query)
                deleted_objects = result.scalars().all()
                deleted_count = len(deleted_objects)
                return deleted_objects, deleted_count         

