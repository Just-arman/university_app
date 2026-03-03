from app.dao.base import BaseDAO
from app.majors.institutes.models import Institute


class InstituteDAO(BaseDAO):
    model = Institute
