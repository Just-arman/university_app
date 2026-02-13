from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload
from app.dao.base import BaseDAO
from app.students.models import Student
from app.majors.models import Major
from app.database import async_session_maker


class MajorsDAO(BaseDAO):
    model = Major

    @classmethod
    async def find_all_majors(cls, **filter_by):
        async with async_session_maker() as session:
            stmt = select(cls.model).filter_by(**filter_by)
            result = await session.execute(stmt)
            return result.scalars().all()


    @classmethod
    async def find_one_major(cls, **filter_by):
        async with async_session_maker() as session:
            stmt = select(cls.model).filter_by(**filter_by)
            result = await session.execute(stmt)
            return result.scalars().one_or_none()


    @classmethod
    async def delete_majors_by_start_id_and_further(cls, start_id: int):
        """
        Удаляет все факультеты с id >= start_id.
        Возвращает количество удалённых записей.
        """
        async with async_session_maker() as session:
            async with session.begin():
                stmt = delete(cls.model).where(cls.model.id >= start_id)
                result = await session.execute(stmt)
            # commit уже выполнен автоматически через session.begin()
            return result.rowcount


    @classmethod
    async def delete_majors_range(cls, start_id: int, end_id: int | None = None):
        """
        Удаляет все факультеты с id в диапазоне [start_id, end_id].
        Если end_id не указан, удаляются все факультеты с start_id и выше.
        Возвращает количество удалённых записей.
        """
        async with async_session_maker() as session:
            async with session.begin():
                if end_id is not None:
                    if start_id > end_id:
                        raise ValueError("start_id не может быть больше end_id")
                    stmt = delete(cls.model).where(cls.model.id >= start_id, cls.model.id <= end_id)
                else:
                    stmt = delete(cls.model).where(cls.model.id >= start_id)

                result = await session.execute(stmt)
            return result.rowcount


    @classmethod
    async def delete_majors_range_with_show_deleted(cls, start_id: int, end_id: int | None = None) -> list[int]:
        """
        Удаляет все факультеты с id в диапазоне [start_id, end_id].
        Если end_id не указан, удаляются все факультеты с start_id и выше.
        Возвращает количество и список удалённых id.
        """
        async with async_session_maker() as session:
            stmt = select(cls.model.id)
            if end_id:
                stmt = stmt.where(cls.model.id.between(start_id, end_id))
            else:
                stmt = stmt.where(cls.model.id >= start_id)
            
            result = await session.execute(stmt)
            ids_to_delete = [row[0] for row in result.fetchall()]
            
            if not ids_to_delete:
                return []
            
            await session.execute(delete(cls.model).where(cls.model.id.in_(ids_to_delete)))
            await session.commit()
            return ids_to_delete
