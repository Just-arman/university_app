from itertools import count
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.dao.base import BaseDAO
from app.majors.dao import MajorsDAO
from app.students.dao import StudentDAO
from app.students.models import Student
from app.students.qp import QueryParamsStudent
from app.students.schemas import SDeleteFilter, SStudentUpdate, SUpdateFilter, StudentFilterSchema, StudentSchema
from app.database import async_session_maker
# from utils import dell_student, upd_student
import os
from typing import List


router = APIRouter(prefix='/students', tags=['Работа со студентами'])


@router.get("/", summary="Получить всех студентов")
async def get_all_students() -> list[StudentSchema]:
    return await StudentDAO.find_all()


@router.get("/get_students_by_filters", summary="Получить студентов по фильтру (фильтрам)")
async def get_all_students_by_filters(query_params: QueryParamsStudent = Depends()) -> list[StudentSchema]:
    return await StudentDAO.find_all(**query_params.to_dict())


# @router.get("/get_one_student_by_filters", summary="Получить одного студента по фильтру (фильтрам)")
# async def get_student_by_filter(request_body: RBStudent = Depends()) -> StudentSchema:
#     result = await StudentDAO.find_all(**request_body.to_dict())
#     if result is None:
#         raise HTTPException(status_code=404, detail=f"Студенты с указанными параметрами не найдены")
#     elif count(result) > 1:
#         return result[0]
#     return result


@router.get("/{id}", summary="Получить одного студента по id")
async def get_student_by_id(id: int) -> StudentSchema | dict:
    result = await StudentDAO.find_one_or_none(id=id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Студент с ID {id} не найден")
    return result


# @router.get("/{id}", summary="Получить одного студента по id")
# async def get_student_by_id(student_id: int) -> StudentSchema | dict:
#     result = await StudentDAO.find_full_data(student_id)
#     if result is None:
#         return {'message': f'Студент с ID {student_id} не найден!'}
#     return result


@router.post("/add_student", summary="Добавить нового студента")
async def add_student_handler(student: StudentSchema):
    student_dict = student.model_dump()
    new_student = await StudentDAO.add_student(student_dict)
    if new_student:
        return {"message": "Студент успешно добавлен!", "Новый студент": new_student}
    raise HTTPException(status_code=400, detail="Ошибка при добавлении студента")


@router.put("/update_student", summary="Обновить информацию о студенте")
async def update_student_handler(student: StudentSchema):
    # student_dict = student.model_dump()
    check = await StudentDAO.update(student)
    if check:
        return {"message": "Информация о студенте успешно обновлена!"}
    raise HTTPException(status_code=400, detail="Ошибка при обновлении информации о студенте")


# @router.put("/update_student")
# async def update_student_handler(filter_student: SUpdateFilter, new_data: SStudentUpdate):
#     check = await upd_student(filter_student.model_dump(), new_data.model_dump())
#     if check:
#         return {"message": "Информация о студенте успешно обновлена!"}
#     raise HTTPException(status_code=400, detail="Ошибка при обновлении информации о студенте")


@router.delete("/delete_student/{student_id}", summary="Удалить студента по id")
async def delete_student(student_id: int) -> dict:
    check = await StudentDAO.delete(id=student_id)
    if check:
        return {"message": f"Студент с ID {student_id} успешно удален!"}
    raise HTTPException(status_code=400, detail="Ошибка при удалении студента")


# @router.delete("/delete_student")
# async def delete_student_handler(filter_student: SDeleteFilter):
#     check = await StudentDAO.delete(filter_student.key, filter_student.value)
#     if check:
#         return {"message": "Студент успешно удален!"}
#     raise HTTPException(status_code=400, detail="Ошибка при удалении студента")


# Получаем путь к директории текущего скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Переходим на уровень выше
parent_dir = os.path.dirname(script_dir)

# Получаем путь к JSON
path_to_json = os.path.join(parent_dir, 'students.json')

# одной строкой
# path_to_json = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'students.json')


# @app.get("/students")
# def get_all_students(course: int | None = None):   
#     students = json_to_dict_list(path_to_json)

#     if course is None:
#         return students

#     # 1. Проверяем, существует ли такой курс вообще
#     courses = {student["course"] for student in students}
#     if course not in courses:
#         raise HTTPException(
#             status_code=404,
#             detail="Указанный курс не найден"
#         )

#     # 2. Если курс существует — выполняем основной код
#     return_list = []
#     for student in students:
#         if student["course"] == course:
#             return_list.append(student)
#     if not return_list:
#         raise HTTPException(status_code=404, detail="На указанном курсе нет студентов")

#     return return_list


# @app.get("/students/{course}")
# def get_all_students_by_course(request_body: RBStudent = Depends()) -> List[StudentSchema]: 
#     students = json_to_dict_list(path_to_json)
#     filtered_students = []
#     for student in students:
#         if student["course"] == request_body.course:
#             filtered_students.append(student)

#     if request_body.major:
#         filtered_students = [student for student in filtered_students if student['major'].lower() == request_body.major.lower()]

#     if request_body.enrollment_year:
#         filtered_students = [student for student in filtered_students if student['enrollment_year'] == request_body.enrollment_year]

#     return filtered_students


# @app.get("/student")
# def get_one_student_by_param(student_id: int) -> StudentSchema:
#     students = json_to_dict_list(path_to_json)

#     # if course is None:
#     #     return students
    
#     for student in students:
#         if student["student_id"] == student_id:
#             return student
#     raise HTTPException(status_code=404, detail="Студент с указанным ID не найден")


# @app.get("/students/{student_id}")
# def get_one_student_by_path(student_id: int) -> StudentSchema:
#     students = json_to_dict_list(path_to_json)

#     for student in students:
#         if student["student_id"] == student_id:
#             return student
#     raise HTTPException(status_code=404, detail="Студент с указанным ID не найден")
