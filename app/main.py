from fastapi import Depends, FastAPI, HTTPException
from app.students.qp import QueryParamsStudent
from app.students.schemas import SDeleteFilter, SStudentUpdate, SUpdateFilter, StudentSchema
from app.students.router import router as router_students
from app.majors.router import router as router_majors
import os
from typing import List, Optional


app = FastAPI()

@app.get("/")
def home_page():
    return {"message": "Привет, Хабр!"}

app.include_router(router_students)
app.include_router(router_majors)
