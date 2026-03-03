


class BaseAppError(Exception):
    status_code: int
    detail: str = "Ошибка приложения"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail


class NotFoundError(BaseAppError):
    status_code = 404
    detail = "Объект не найден"


class BadRequestError(BaseAppError):
    status_code = 400
    detail = "Некорректный запрос"


class ConflictError(BaseAppError):
    status_code = 409
    detail = "Конфликт данных"