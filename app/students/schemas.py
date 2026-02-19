import re
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from app.enums import MajorEnum


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

    @model_validator(mode="before")
    def check_names_present(cls, values):
        if not values.get("major_name"):
            raise ValueError("major_name обязателен")
        if not values.get("institute_name"):
            raise ValueError("institute_name обязателен")
        return values
    

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date):
        if value and value >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return value
