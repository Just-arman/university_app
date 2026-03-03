from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import func, insert, select
from sqlalchemy import update as sqlalchemy_update

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions import BadRequestError, NotFoundError
from app.majors.institutes.models import Institute
from app.majors.models import Major
from app.students.models import Student


class StudentDAO(BaseDAO):
    model = Student

    @classmethod
    async def add_student(cls, student_data: dict):
        async with async_session_maker() as session:
            async with session.begin():
                # Получаем объект major
                major_name = student_data.get("major_name")
                if not major_name:
                    raise BadRequestError("Поле major_name обязательно")

                result = await session.execute(
                    select(Major).where(Major.major_name == major_name)
                )
                major = result.scalar_one_or_none()
                if major is None:
                    raise NotFoundError(f"Специальность '{major_name}' не была найдена")

                # Получаем объект institute
                institute_name = student_data.get("institute_name")
                if not institute_name:
                    raise BadRequestError("Поле institute_name обязательно")

                result = await session.execute(
                    select(Institute).where(Institute.institute_name == institute_name)
                )
                institute = result.scalar_one_or_none()
                if institute is None:
                    raise NotFoundError(f"Институт '{institute_name}' не был найден")

                # Убираем ненужные поля, чтобы SQLAlchemy не ругался
                student_data_clean = {k: v for k, v in student_data.items() if k not in ("major_name", "institute_name")}
                student_data_clean["major_id"] = major.id
                student_data_clean["institute_id"] = institute.id

                # Проверяем, нет ли в бд студента с таким же id
                student_id = student_data_clean.get("id")
                if student_id is not None:
                    query = select(cls.model.id).where(cls.model.id == student_id)
                    result = await session.execute(query)
                    existing_id = result.scalar_one_or_none()
                    if existing_id :
                        raise BadRequestError(f"Студент с id={student_id} уже существует")
                    
                # Если студента с таким id еще нет, то добавляем
                stmt = (
                    insert(cls.model)
                    .values(**student_data_clean)
                    .returning(cls.model.id, cls.model.major_id, cls.model.institute_id)
                )
                result = await session.execute(stmt)
                new_student_id, major_id, institute_id = result.fetchone()

                # Увеличиваем счётчик студентов для специальности и института
                await session.execute(
                    sqlalchemy_update(Major)
                    .where(Major.id == major_id)
                    .values(count_students=Major.count_students + 1)
                )

                await session.execute(
                    sqlalchemy_update(Institute)
                    .where(Institute.id == institute_id)
                    .values(count_students=Institute.count_students + 1)
                )

                return new_student_id
            

    @classmethod
    async def delete_student(cls, **student_data):
        if not student_data:
            raise ValueError("Необходимо указать хотя бы один параметр для удаления студента")

        async with async_session_maker() as session:
            async with session.begin():
                # Находим студента
                query = (
                    select(
                        cls.model.id,
                        cls.model.major_id,
                        cls.model.institute_id,
                    ).filter_by(**student_data)
                )
                
                result = await session.execute(query)
                student = result.first()  # возвращает tuple (id, major_id, institute_id)

                if not student:
                    raise NotFoundError(f"Студент с параметром {student_data} не найден")
                
                student_id, major_id, institute_id = student

                # Удаляем студента
                await session.execute(
                    sqlalchemy_delete(cls.model).where(cls.model.id == student_id)
                )

                # Уменьшаем счетчик студентов по специальности и институту
                await session.execute(
                    sqlalchemy_update(Major)
                    .where(Major.id == major_id)
                    .values(count_students=func.greatest(Major.count_students - 1, 0))
                )
                await session.execute(
                    sqlalchemy_update(Institute)
                    .where(Institute.id == institute_id)
                    .values(count_students=func.greatest(Institute.count_students - 1, 0))
                )

                return True
            
