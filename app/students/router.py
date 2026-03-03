from fastapi import APIRouter, Depends, HTTPException

from app.students.dao import StudentDAO
from app.students.qp import QueryParamsStudent
from app.students.schemas import StudentSchema


router = APIRouter(prefix='/students', tags=['Работа со студентами'])


@router.get("/", summary="Получить всех студентов")
async def get_all_students() -> list[StudentSchema]:
    return await StudentDAO.find_all()


@router.get("/get_students_by_filters", summary="Получить студентов по фильтру (фильтрам)")
async def get_all_students_by_filters(query_params: QueryParamsStudent = Depends()) -> list[StudentSchema]:
    return await StudentDAO.find_all(**query_params.to_dict())


@router.get("/{id}", summary="Получить одного студента по id")
async def get_student_by_id(id: int) -> StudentSchema | dict:
    result = await StudentDAO.find_one_or_none(id=id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Студент с ID {id} не найден")
    return result


@router.post("/add_student", summary="Добавить нового студента")
async def add_student_handler(student_data: StudentSchema):
    student_dict = student_data.model_dump()
    new_student = await StudentDAO.add_student(student_dict)
    if new_student:
        return {"message": "Студент успешно добавлен!", "Новый студент": student_data}
    raise HTTPException(status_code=400, detail="Ошибка при добавлении студента")


@router.put("/update_student", summary="Обновить информацию о студенте")
async def update_student_handler(student: StudentSchema):
    check = await StudentDAO.update(student)
    if check:
        return {"message": "Информация о студенте успешно обновлена!"}
    raise HTTPException(status_code=400, detail="Ошибка при обновлении информации о студенте")


@router.delete("/{student_id}", summary="Удалить студента по id")
async def delete_student_handler(student_id: int) -> dict:
    await StudentDAO.delete_student(id=student_id)
    return {"message": f"Студент с ID {student_id} успешно удален!"}
