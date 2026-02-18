from fastapi import HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app.dao.base import BaseDAO
from app.majors.models import Major
from app.students.models import Student
from app.database import async_session_maker
from enums import MajorEnum


class StudentDAO(BaseDAO):
    model = Student

    @classmethod
    async def find_full_data(cls, student_id: int):
        async with async_session_maker() as session:
            # Запрос для получения информации о студенте вместе с информацией о специальности
            query = select(cls.model).options(joinedload(cls.model.major)).filter_by(id=student_id)
            result = await session.execute(query)
            student_info = result.scalar_one_or_none()

            # Если студент не найден, возвращаем None
            if not student_info:
                return None

            student_data = student_info.to_dict()
            student_data['major'] = student_info.major.major_name
            return student_data
        
    # @classmethod
    # async def add_student(cls, student_data: dict):
    #     async with async_session_maker() as session:
    #         async with session.begin():
    #             # Вставка нового студента
    #             stmt = insert(cls.model).values(**student_data).returning(cls.model.id, cls.model.major_id)
    #             result = await session.execute(stmt)
    #             new_student_id, major_id = result.fetchone()

    #             # Увеличение счетчика студентов в таблице Major
    #             update_major = (
    #                 update(Major)
    #                 .where(Major.id == major_id)
    #                 .values(count_students=Major.count_students + 1)
    #             )
    #             await session.execute(update_major)

    #             try:
    #                 await session.commit()
    #             except SQLAlchemyError as e:
    #                 await session.rollback()
    #                 raise e

    #             return new_student_id
            

    @classmethod
    async def add_student(cls, student_data: dict):
        async with async_session_maker() as session:
            async with session.begin():
                # 1. Получаем специальность по названию
                major_enum = student_data.pop("major_name")  # достаем поле major из словаря
                if isinstance(major_enum, MajorEnum):
                    major_name = major_enum.value
                else:
                    major_name = major_enum
                print(f"{major_name=}")
                if not major_name:
                    raise HTTPException(status_code=400, detail="Поле major_name обязательно")
                
                result = await session.execute(
                    select(Major.id).where(Major.major_name == major_name)
                )
                major_id = result.scalar_one_or_none()
                if major_id is None:
                    raise ValueError(f"Специальностей с названием '{major_name}' не найдено")

                student_data["major_id"] = major_id

                # 2. Добавляем нового студента
                stmt = insert(cls.model).values(**student_data).returning(cls.model.id, cls.model.major_id)
                result = await session.execute(stmt)
                new_student_id, major_id = result.fetchone()
                
                # 3. Увеличиваем счётчик студентов, обучающихся по специальности
                update_major = (
                    update(Major)
                    .where(Major.id == major_id)
                    .values(count_students=Major.count_students + 1)
                )
                await session.execute(update_major)

                try:
                    await session.commit()
                except SQLAlchemyError as e:    
                    await session.rollback()
                    raise HTTPException(status_code=400, detail=f"Ошибка при добавлении студента: {e}")

                return new_student_id
