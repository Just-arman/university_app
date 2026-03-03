from fastapi import APIRouter, Depends, HTTPException, Query
from app.majors.dao import MajorDAO
from app.majors.qp import QueryParamsMajor
from app.majors.schemas import SMajorAdd, SMajorResponse, SMajorResponseList, SMajorsRead, SMajorsUpdate


router = APIRouter(prefix='/majors', tags=['Работа со специальностями (профилями обучения)'])


@router.get("/", summary="Получить все специальности")
async def get_all_majors() -> list[SMajorsRead]:
    majors = await MajorDAO.find_all_majors()
    return majors


@router.get("", summary="Получить специальность по фильтру (фильтрам) или все")
async def get_major_by_filters(query_params: QueryParamsMajor = Depends()) -> SMajorResponseList | list[SMajorsRead]:
    filters = query_params.to_dict()
    majors = await MajorDAO.find_all_majors(**filters)
    if not majors:
        raise HTTPException(status_code=404, detail="Специальности с указанными фильтрами не найден")
    if not filters:
        return {"message": "Специальности не указаны, поэтому выдаются все специальности!", "majors": majors}
    return majors


@router.post("", summary="Добавить новую специальность")
async def register_major(major: SMajorAdd) -> SMajorResponse:
    new_major = await MajorDAO.add(**major.model_dump())
    if not new_major:
        raise HTTPException(status_code=400, detail="Ошибка при добавлении")
    return {
        "message": "Специальность успешно добавлена!",
        "major": new_major
    }


@router.put("/{major_id}", summary="Обновить специальность")
async def update_major_by_id(major_id: int, major: SMajorsUpdate) -> SMajorResponse:
    # update_data = {k: v for k, v in major.model_dump().items() if k != "id"}
    update_data = major.model_dump(exclude={"id"})
    print(f"{update_data=}")
    if not update_data:
        raise HTTPException(status_code=400, detail="Не переданы данные для обновления")
    updated_major = await MajorDAO.update(filter_by={"id": major_id}, **update_data)

    if not updated_major:
        new_major = await MajorDAO.add(id=major.id, **update_data)
        if not new_major:
            raise HTTPException(status_code=400, detail="Ошибка при создании специальности")
        return {
            "message": "Создана новая специальность, потому что специальность с указанным ID не была найдена",
            "major": new_major
        }

    return {
        "message": "Специальность успешно обновлена",
        "major": updated_major
    }


@router.patch("/{major_id}", summary="Обновить специальность")
async def update_major_by_id(major_id: int, major: SMajorsUpdate) -> SMajorResponse:
    update_data = {k: v for k, v in major.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Не переданы данные для обновления")
    updated_major = await MajorDAO.update(filter_by={"id": major_id}, **update_data)
    if not updated_major:
        raise HTTPException(status_code=404, detail="Специальность с таким ID не найдена")
    return {
        "message": "Специальность успешно обновлена!",
        "major": updated_major
    }


@router.delete("/{major_id}", summary="Удалить специальность по ID")
async def delete_major(major_id: int) -> dict:
    deleted_major = await MajorDAO.delete(id=major_id)
    if deleted_major:
        return {"message": f"Специальность с ID {major_id} удалена!"}
    else:
        return {"message": "Ошибка при удалении специальность!"}


@router.delete("", summary="Удалить специальности по диапазону ID или все")
async def delete_majors(
    start_id: int | None = Query(None, ge=1, description="ID начала диапазона включительно"),
    end_id: int | None = Query(None, ge=1, description="ID конца диапазона включительно")
):
    try:
        deleted_majors = await MajorDAO.delete_majors_range(start_id, end_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not deleted_majors:
        range_desc = f"{start_id}-{end_id}" if end_id else f"{start_id}-∞"
        raise HTTPException(status_code=404, detail=f"Нет специальностей с id в диапазоне: {range_desc}")

    range_desc = f"{start_id}-{end_id}" if end_id else f"{start_id}-∞"
    return {
        "message": f"Удалено {len(deleted_majors)} специальностей с id в диапазоне: {range_desc}",
        "deleted_ids": deleted_majors
    }


@router.post("/sync-enums", summary="Синхронизировать значения majors и institutes в бд со значениями enums")
async def sync_majors_and_institutes_with_enums():
    try:
        result = await MajorDAO.sync_with_enums()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    category = result.get("category")

    if category == "majors":
        return {
            "category": "majors",
            "message": "Обнаружены несоответствия в специализациях. База данных обновлена.",
            "added_majors": result["added"],
            "deleted_majors": result["deleted"],
        }

    if category == "institutes":
        if result.get("synced"):
            return {
                "message": "Majors и institutes уже синхронизированы с enums."
            }

        return {
            "category": "institutes",
            "message": "Обнаружены несоответствия в институтах. База данных обновлена.",
            "added_institutes": result["added"],
            "deleted_institutes": result["deleted"],
        }

    raise HTTPException(status_code=500, detail="Ошибка при синхронизации")

