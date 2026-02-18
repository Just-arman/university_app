from fastapi import APIRouter, Depends, HTTPException, Query
from app.dao.base import BaseDAO
from app.majors.institutes.dao import InstituteDAO


router = APIRouter(prefix='/institutes', tags=['Работа с институтами'])

