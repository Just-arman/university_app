from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, str_uniq, int_pk



class Institute(Base):
    id: Mapped[int_pk]
    institute_name: Mapped[str_uniq]
    major_id: Mapped[int] = mapped_column(ForeignKey("majors.id"), nullable=False)
    count_students: Mapped[int] = mapped_column(server_default=text('0'))

    major: Mapped["Major"] = relationship("Major", back_populates="institutes")
    students: Mapped[list["Student"]] = relationship("Student", back_populates="institute")
    

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, institute_name={self.institute_name!r})"

    def __repr__(self):
        return str(self)