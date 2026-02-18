from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, str_uniq, int_pk


# создаем модель таблицы специальностей (majors)
class Major(Base):
    id: Mapped[int_pk]
    major_name: Mapped[str_uniq]
    count_students: Mapped[int] = mapped_column(server_default=text('0'))

    institutes: Mapped[list["Institute"]] = relationship("Institute", back_populates="major")
    # institutes: Mapped[list["Institute"]] = relationship("Institute", back_populates="major", lazy="selectin")
    students: Mapped[list["Student"]] = relationship("Student", back_populates="major")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, major_name={self.major_name!r})"

    def __repr__(self):
        return str(self)
        