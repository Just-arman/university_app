from sqlalchemy import select, delete as sqlalchemy_delete
from app.dao.base import BaseDAO
from app.majors.models import Major
from app.database import async_session_maker
from enums import MajorDescriptionEnum, MajorNameEnum



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
        enum_names = {e.value for e in MajorNameEnum}

        async with async_session_maker() as session:
            async with session.begin():
                # получаем текущие значения в БД
                result = await session.execute(select(cls.model))
                db_majors = result.scalars().all()

                db_names = {m.major_name for m in db_majors}
                enum_names = {e.value for e in MajorNameEnum}

                # получаем разницу
                to_add = enum_names - db_names
                to_delete = db_names - enum_names

                # если всё уже синхронизировано
                if not to_add and not to_delete:
                    return {
                        "synced": True,
                        "added": [],
                        "deleted": [],
                    }
                
                # если есть лишее, удаляем
                if to_delete:
                    stmt_delete = (
                        sqlalchemy_delete(cls.model)
                        .where(cls.model.major_name.in_(to_delete))
                    )
                    await session.execute(stmt_delete)

                # если есть недостающее, добавляем
                new_objects = []
                for enum_item in MajorNameEnum:
                    if enum_item.value in to_add:
                        description = MajorDescriptionEnum[enum_item.name].value

                        new_objects.append(
                            cls.model(
                                major_name=enum_item.value,
                                major_description=description,
                            )
                        )

                if new_objects:
                    session.add_all(new_objects)

                return {
                    "synced": False,
                    "added": list(to_add),
                    "deleted": list(to_delete),
                }