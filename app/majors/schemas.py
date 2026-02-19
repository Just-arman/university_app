from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.enums import institutes_enum


class SMajorsRead(BaseModel):
    id: int
    major_name: str = Field(description="Название специальности")
    institute_name: str = Field(description="Название института")
    count_students: int = Field(0, description="Количество студентов на специальности")

    model_config = ConfigDict(from_attributes=True)


class SMajorAdd(BaseModel):
    major_name: str
    institute_name: str | None = None
    count_students: int = 0

    model_config = ConfigDict(from_attributes=True)

    @field_validator("institute_name")
    def check_institute(cls, v, values):
        major = values.get("major")
        if major and v not in institutes_enum[major]:
            raise ValueError(f"{v} не является допустимым институтом для {major.value}")
        return v    


class SMajorsUpdate(BaseModel):
    major_name: str | None


class SMajorResponse(BaseModel):
    message: str | None = None
    major: SMajorsRead


class SMajorResponseList(BaseModel):
    message: str | None = None
    majors: list[SMajorsRead]
