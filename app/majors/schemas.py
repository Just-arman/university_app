from pydantic import BaseModel, ConfigDict, Field


class SMajorsRead(BaseModel):
    id: int
    major_name: str = Field(description="Название специальности")
    major_description: str | None = Field(None, description="Описание специальности")
    count_students: int = Field(0, description="Количество студентов на специальности")

    model_config = ConfigDict(from_attributes=True)


class SMajorAdd(BaseModel):
    major_name: str
    major_description: str | None = None
    count_students: int = 0


class SMajorsUpdate(BaseModel):
    major_name: str | None
    major_description: str | None = None


class SMajorResponse(BaseModel):
    message: str | None = None
    major: SMajorsRead


class SMajorResponseList(BaseModel):
    message: str | None = None
    majors: list[SMajorsRead] 
