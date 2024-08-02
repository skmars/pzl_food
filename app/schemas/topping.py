from pydantic import (
    BaseModel,
    Field,
)

from pzl_food.config import settings


class ToppingSchema(BaseModel):
    """Схема ингредиентов"""

    id: int
    name: str = Field(max_length=settings.VALIDATION.name_topping_limit)
