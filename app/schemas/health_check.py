from pydantic import BaseModel


class HealthCheckResponseSchema(BaseModel):
    """
    Схема проверки работоспособности сервера
    """

    status_code: int
    detail: str
