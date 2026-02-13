from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SMajorsRead(BaseModel):
    id: int
    major_name: str = Field(description="Название факультета")
    major_description: str = Field(None, description="Описание факультета")
    count_students: int = Field(0, description="Количество студентов")

    model_config = ConfigDict(from_attributes=True)


class SMajorResponse(BaseModel):
    message: str
    major: SMajorsRead


class SMajorsAdd(BaseModel):
    major_name: str = Field(description="Название факультета")
    major_description: str = Field(None, description="Описание факультета")
    count_students: int = Field(0, description="Количество студентов")


class SMajorsUpdName(BaseModel):
    major_name: str = Field(description="Новое название факультета")
    major_description: str = Field(None, description="Новое описание факультета")


class SMajorsUpdDesc(BaseModel):
    major_name: str = Field(description="Название факультета")
    major_description: str = Field(None, description="Новое описание факультета")