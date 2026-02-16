from sqlalchemy import select, delete as sqlalchemy_delete
from app.dao.base import BaseDAO
from app.majors.models import Major
from app.database import async_session_maker
from enums import MajorEnum



class MajorsDAO(BaseDAO):
    model = Major

    @classmethod
    async def find_all_majors(cls, **filter_by):
        async with async_session_maker() as session:
            stmt = select(cls.model).filter_by(**filter_by).order_by(cls.model.id)
            result = await session.execute(stmt)
            return result.scalars().all()
            

    @classmethod
    async def find_one_major(cls, **filter_by):
        async with async_session_maker() as session:
            filter_by = {k: v for k, v in filter_by.items() if v is not None}
            stmt = select(cls.model).filter_by(**filter_by)
            result = await session.execute(stmt)
            return result.scalars().one_or_none()


    @classmethod
    async def delete_majors_range(cls, start_id: int | None = None, end_id: int | None = None):       
        async with async_session_maker() as session:
            async with session.begin():
                stmt = sqlalchemy_delete(cls.model)
                if start_id is not None and end_id is not None:
                    # stmt = stmt.where(cls.model.id >= start_id, cls.model.id <= end_id)
                    stmt = stmt.where(cls.model.id.between(start_id, end_id))
                elif start_id is not None:
                    stmt = stmt.where(cls.model.id >= start_id)

                stmt = stmt.returning(cls.model)
                result = await session.execute(stmt)
                return result.scalars().all()


    @classmethod
    async def sync_with_enum(cls) -> dict:
        enum_values = {e.value for e in MajorEnum}

        async with async_session_maker() as session:
            async with session.begin():
                # получаем текущие значения в БД
                result = await session.execute(select(cls.model.major_name))
                db_values = set(result.scalars().all())

                # получаем разницу
                to_add = enum_values - db_values
                to_delete = db_values - enum_values

                # если всё уже синхронизировано
                if not to_add and not to_delete:
                    return {
                        "synced": True,
                        "added": [],
                        "deleted": [],
                    }

                # удаляем лишние
                if to_delete:
                    await session.execute(
                        sqlalchemy_delete(cls.model)
                        .where(cls.model.major_name.in_(to_delete))
                    )

                # добавляем недостающие
                new_objects = [
                    cls.model(major_name=name)
                    for name in to_add
                ]
                session.add_all(new_objects)

                return {
                    "synced": False,
                    "added": list(to_add),
                    "deleted": list(to_delete),
                }