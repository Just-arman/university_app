from typing import Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, ValidationError
from datetime import date, datetime
from enums import MajorEnum, institutes_enum
import re


class StudentSchema(BaseModel):
    id: int
    first_name: str = Field(min_length=1, max_length=50, description="Имя студента, от 1 до 50 символов")
    last_name: str = Field(min_length=1, max_length=50, description="Фамилия студента, от 1 до 50 символов")
    date_of_birth: date = Field(description="Дата рождения студента в формате ГГГГ-ММ-ДД")
    phone_number: str = Field(description="Номер телефона в международном формате, начинающийся с '+'")
    email: EmailStr = Field(description="Электронная почта студента")
    address: str = Field(min_length=10, max_length=200, description="Адрес студента, не более 200 символов")
    enrollment_year: int = Field(ge=2002, le=2023, description="Год поступления должен быть не меньше 2002")
    course: int = Field(ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    special_notes: str | None = Field(None, max_length=500, description="Дополнительные заметки, не более 500 символов")
    major_name: MajorEnum = Field(description="Название специальности")
    institute_name: str = Field(description="Название института")
                                         
    model_config = ConfigDict(from_attributes=True)

    # @field_validator("institute_name")
    # def check_institute(cls, v, values):
    #     major = values.get("major")
    #     if major and v not in institutes_enum[major]:
    #         raise ValueError(f"{v} не является допустимым институтом для {major.value}")
    #     return v

    # @field_validator("phone_number")
    # @classmethod
    # def validate_phone_number(cls, value: str) -> str:
    #     if not re.match(r'^\+\d{1,15}$', value):
    #         raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
    #     return value

    # @field_validator("date_of_birth")
    # @classmethod
    # def validate_date_of_birth(cls, value: date):
    #     if value and value >= datetime.now().date():
    #         raise ValueError('Дата рождения должна быть в прошлом')
    #     return value


class SStudentFilter(BaseModel):
    student_id: int | None = None
    major_name: str | None = None
    institute_name: int | None = None
    course: int | None = None
    enrollment_year: int | None = None


class SUpdateFilter(BaseModel):
    id: int


class SStudentUpdate(BaseModel):
    course: int = Field(ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    major_name: MajorEnum | None = Field(description="Название специальности")
    institute_name: str | None = Field(description="Название института")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("institute_name")
    def check_institute(cls, v, values):
        major = values.get("major")
        if major and v not in institutes_enum[major]:
            raise ValueError(f"{v} не является допустимым институтом для {major.value}")
        return v        


class SDeleteFilter(BaseModel):
    key: str
    value: Any