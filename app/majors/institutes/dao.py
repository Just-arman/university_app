from sqlalchemy import select, delete as sqlalchemy_delete
from app.database import async_session_maker
from app.dao.base import BaseDAO
from app.majors.institutes.models import Institute
from enums import MajorEnum, institutes_enum


class InstituteDAO(BaseDAO):
    model = Institute
