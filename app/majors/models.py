from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, int_pk, str_uniq


class Major(Base):
    id: Mapped[int_pk]
    major_name: Mapped[str_uniq]
    count_students: Mapped[int] = mapped_column(server_default=text('0'))

    institutes: Mapped[list["Institute"]] = relationship("Institute", back_populates="major")
    students: Mapped[list["Student"]] = relationship("Student", back_populates="major")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, major_name={self.major_name!r})"

    def __repr__(self):
        return str(self)
        