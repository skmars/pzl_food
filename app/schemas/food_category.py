from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
)

from app.schemas import ResponseFoodSchema
from pzl_food.config import settings


class ResponseFoodCategorySchema(BaseModel):
    """Схема категорий блюд"""

    id: int
    name: str = Field(max_length=settings.VALIDATION.name_food_category_limit)
    is_published: bool
    foods: Optional[List[ResponseFoodSchema]] = None
