from http import HTTPStatus


class APIError(Exception):
    """Кастомный класс исключения для ошибок API."""

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = message
        self.status_code = status_code
