from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import select

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.enums import MajorEnum, institutes_enum
from app.majors.institutes.models import Institute
from app.majors.models import Major


class MajorDAO(BaseDAO):
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
    async def sync_with_enums(cls) -> dict:
        if set(institutes_enum.keys()) != set(MajorEnum):
            raise ValueError("institutes_enum и MajorEnum не совпадают")

        async with async_session_maker() as session:
            async with session.begin():

                # Получаем majors из БД
                result = await session.execute(select(cls.model))
                db_majors = result.scalars().all()
                db_major_names = {m.major_name: m for m in db_majors}

                enum_major_names = {e.value for e in MajorEnum}

                to_add_majors = enum_major_names - set(db_major_names.keys())
                to_delete_majors = set(db_major_names.keys()) - enum_major_names

                if to_add_majors or to_delete_majors:

                    # удаляем лишние majors
                    for major_name in to_delete_majors:
                        major = db_major_names[major_name]

                        await session.execute(
                            sqlalchemy_delete(Institute).where(
                                Institute.major_id == major.id
                            )
                        )
                        await session.delete(major)

                    # добавляем недостающие majors
                    for major_name in to_add_majors:
                        session.add(cls.model(major_name=major_name))

                    return {
                        "category": "majors",
                        "synced": False,
                        "added": list(to_add_majors),
                        "deleted": list(to_delete_majors),
                    }

                # Если majors ОК — проверяем institutes
                institutes_added: list[str] = []
                institutes_deleted: list[str] = []

                for major_enum in MajorEnum:
                    major_name = major_enum.value
                    major = db_major_names[major_name]

                    # безопасно получаем институты
                    result_inst = await session.execute(
                        select(Institute).where(Institute.major_id == major.id)
                    )
                    db_institutes = result_inst.scalars().all()
                    db_institute_names = {i.institute_name for i in db_institutes}

                    enum_institutes = set(institutes_enum.get(major_enum, []))

                    # удаляем лишние institutes, если есть
                    for inst in db_institutes:
                        if inst.institute_name not in enum_institutes:
                            await session.delete(inst)
                            institutes_deleted.append(inst.institute_name)

                    # добавляем недостающие institutes, если не хватает
                    for name in enum_institutes - db_institute_names:
                        session.add(
                            Institute(
                                institute_name=name,
                                major_id=major.id,
                            )
                        )
                        institutes_added.append(name)

                return {
                    "category": "institutes",
                    "synced": not institutes_added and not institutes_deleted,
                    "added": institutes_added,
                    "deleted": institutes_deleted,
                }
