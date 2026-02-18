

class QueryParamsStudent:
    def __init__(self, student_id: int | None = None,
                 major_name: int | None = None,
                 institute_name: int | None = None,
                 course: int | None = None,
                 enrollment_year: int | None = None):
        self.id = student_id
        self.major_name = major_name
        self.institute_name = institute_name
        self.course = course
        self.enrollment_year = enrollment_year

        
    def to_dict(self) -> dict:
        data = {
            'id': self.id, 
            'major_name': self.major_name,
            'institute_name': self.institute_name,
            'course': self.course,
            'enrollment_year': self.enrollment_year
        }
        # Создаем словарь с исключением None-значений
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data