from sqlalchemy import delete
from app.logger import log
from fastapi import APIRouter, Depends, HTTPException, Query
from app.majors.dao import MajorsDAO
from app.majors.models import Major
from app.majors.qp import QueryParamsMajor
from app.majors.schemas import SMajorResponse, SMajorsAdd, SMajorsRead, SMajorsUpdDesc, SMajorsUpdName
from app.database import async_session_maker


router = APIRouter(prefix='/majors', tags=['Работа с факультетами'])


@router.get("/", summary="Получить все факультеты")
async def get_all_majors() -> list[SMajorsRead]:
    majors = await MajorsDAO.find_all_majors()
    if not majors:
        return []
    return majors


@router.get("/get_major_by_filters/", summary="Получить факультет по любому из фильтров")
async def get_major(major: SMajorsRead) -> SMajorsRead | dict:
    majors = await MajorsDAO.find_all_majors(**major.model_dump())
    log.info(f"{majors=}")
    major_dicts = [m.to_dict() for m in majors]
    major_dicts = majors.to_dict()
    if majors:
        return {"message": "Факультет успешно получен!", "majors": major_dicts}
    else:
        return {"message": "Ошибка при получении факультета!"}


@router.get("/get_major_by_id_or_name/", summary="Получить факультет по ID или названию")
async def get_major_by_id_or_name(major_id: int | None = None, major_name: str | None = None) -> SMajorsRead:
    if major_id is None and major_name is None:
        raise HTTPException(status_code=400, detail="Необходимо указать major_id или major_name")
    
    # вариант 1
    # filters = {}
    # if major_id is not None:
    #     filters["id"] = major_id
    # if major_name is not None:
    #     filters["major_name"] = major_name

    # вариант 2
    filters_data = {"id": major_id, "major_name": major_name}
    filters = {}
    for key, value in filters_data.items():
        if value is not None:
            filters[key] = value

    major = await MajorsDAO.find_one_major(**filters)
    log.info(f"{major=}")
    if not major:
        raise HTTPException(status_code=404, detail="Факультет не найден")
    return major


# @router.get("/get_major_by_id_or_name/", summary="Получить факультет по ID или названию")
# async def get_major_by_id_or_name(query_params: QueryParamsMajor = Depends()) -> SMajorsRead:
#     major = await MajorsDAO.find_one_major(**query_params.to_dict())
#     log.info(f"{major=}")
#     if not major:
#         raise HTTPException(status_code=404, detail="Факультет не найден")
#     return major


@router.get("/get/{major_id}/", summary="Получить факультет по ID")
async def get_major_by_id(major_id: int) -> SMajorsRead:
    major = await MajorsDAO.find_one_major(id=major_id)
    log.info(f"{major=}")
    if not major:
        raise HTTPException(status_code=404, detail="Факультет не найден")
    return major


@router.post("/add_major/", summary="Добавить новый факультет")
async def register_major(major: SMajorsAdd) -> SMajorResponse:
    new_major = await MajorsDAO.add(**major.model_dump())
    log.info(f"{new_major=}")
    if not new_major:
        raise HTTPException(status_code=400, detail="Ошибка при добавлении")
    return {
        "message": "Факультет успешно добавлен!",
        "major": new_major
    }


@router.put("/update_major_name/", summary="Обновить название конкретного факультета")
async def update_major_name(major: SMajorsUpdName) -> dict:
    check = await MajorsDAO.update(filter_by={'major_name': major.major_name},
                                   major_description=major.major_description)
    if check:
        return {"message": "Название факультета успешно обновлено!", "major": major}
    else:
        return {"message": "Ошибка при обновлении названия факультета!"}


@router.put("/update_description/", summary="Обновить описание конкретного факлуьтета")
async def update_major_description(major: SMajorsUpdDesc) -> dict:
    check = await MajorsDAO.update(filter_by={'major_name': major.major_name},
                                   major_description=major.major_description)
    if check:
        return {"message": "Описание факультета успешно обновлено!", "major": major}
    else:
        return {"message": "Ошибка при обновлении описания факультета!"}


@router.delete("/delete/{major_id}", summary="Удалить факультет по ID")
async def delete_major(major_id: int) -> dict:
    check = await MajorsDAO.delete(id=major_id)
    if check:
        return {"message": f"Факультет с ID {major_id} удален!"}
    else:
        return {"message": "Ошибка при удалении факультета!"}


@router.delete("/delete_majors_range/", summary="Удалить факультеты по диапазону ID")
async def delete_majors_range(
    start_id: int = Query(..., ge=1, description="ID начала диапазона включительно"),
    end_id: int | None = Query(None, ge=1, description="ID конца диапазона включительно (необязательно)")
):
    try:
        deleted_count = await MajorsDAO.delete_majors_range(start_id, end_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if deleted_count == 0:
        range_desc = f"{start_id}-{end_id}" if end_id else f"{start_id}-∞"
        raise HTTPException(status_code=404, detail=f"Нет факультетов с id со значениями в диапазоне {range_desc}")

    range_desc = f"{start_id}-{end_id}" if end_id else f"{start_id}-∞"
    return {"message": f"Удалено {deleted_count} факультетов с id со значениями в диапазоне {range_desc}"}


@router.delete("/delete_majors_range_with_show_deleted/", summary="Удалить факультеты по диапазону ID")
async def delete_majors_range_with_show_deleted(
    start_id: int = Query(..., ge=1, description="ID начала диапазона включительно"),
    end_id: int | None = Query(None, ge=1, description="ID конца диапазона включительно (необязательно)")
):
    try:
        deleted_ids = await MajorsDAO.delete_majors_range_with_show_deleted(start_id, end_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not deleted_ids:
        range_desc = f"{start_id}-∞" if end_id is None else f"{start_id}-{end_id}"
        raise HTTPException(status_code=404, detail=f"Нет факультетов с id в диапазоне {range_desc}")

    range_desc = f"{start_id}-∞" if end_id is None else f"{start_id}-{end_id}"
    return {
        "message": f"Удалено {len(deleted_ids)} факультетов с id в диапазоне {range_desc}",
        "deleted_ids": deleted_ids
    }


@router.delete("/delete/", summary="Удалить все факультеты")
async def delete_major() -> dict:
    check = await MajorsDAO.delete()
    if check:
        return {"message": f"Все факультеты удалены!"}
    else:
        return {"message": "Ошибка при удалении факультетов!"}