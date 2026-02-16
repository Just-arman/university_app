


class QueryParamsMajor:
    def __init__(self,
                 major_id: int | None = None,
                 major_name: str | None = None,
                 count_students: int | None = None):
        self.id = major_id
        self.major_name = major_name
        self.count_students = count_students

    def to_dict(self) -> dict:
        filters_data = {
            "id": self.id, 
            "major_name": self.major_name,
            "count_students": self.count_students
        }
        # Убираем None-значения
        filters = {
            key: value for key, value in filters_data.items()
            if value is not None
        }
        return filters