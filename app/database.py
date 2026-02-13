from datetime import datetime
import keyword
from typing import Annotated
from sqlalchemy import func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from app.config import get_db_url


# DB_HOST = 'localhost'
# DB_PORT = '5435'
# DB_NAME = 'students_db'
# DB_USER = 'admin'
# DB_PASSWORD = 'postgres'

DATABASE_URL = get_db_url()
engine = create_async_engine(DATABASE_URL)
# engine = create_async_engine(DATABASE_URL, connect_args={"options": "-csearch_path=public"})
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# настройка аннотаций
int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]