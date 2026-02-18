from pydantic import BaseModel, ConfigDict, Field, field_validator
from enums import institutes_enum


class SInstitutesRead(BaseModel):
    id: int
    institute_name: str = Field(description="Название института")
    major_name: str = Field(description="Название специальности") 
    count_students: int = Field(0, description="Количество студентов в институте")

    model_config = ConfigDict(from_attributes=True)


class SInstituteAdd(BaseModel):
    institute_name: str
    major_name: str
    count_students: int = 0

    model_config = ConfigDict(from_attributes=True)

    @field_validator("institute_name")
    def check_institute(cls, v, values):
        major = values.get("major")
        if major and v not in institutes_enum[major]:
            raise ValueError(f"{v} не является допустимым институтом для {major.value}")
        return v    