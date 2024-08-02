from typing import (
    List,
    Optional,
)

from fastapi import HTTPException
from pydantic import (
    BaseModel,
    Field,
    validator,
)

from app.schemas import ToppingSchema
from pzl_food.config import settings


class BaseFoodSchema(BaseModel):
    """Схема блюда"""

    description: str = Field(max_length=settings.VALIDATION.food_description_limit)
    price: int
    is_special: bool
    is_vegan: bool
    is_published: bool  # я понимаю это как блюдо уже заявлено - да/нет
    category_id: Optional[int] = None
    toppings: List[ToppingSchema]

    @validator("price")
    def validate_price(cls, value):
        if value < settings.VALIDATION.food_low_price_limit:
            raise HTTPException(
                status_code=422,
                detail=("Цена блюда меньше допустимого: %s!", settings.VALIDATION.food_low_price_limit),
            )
        return value


class RequestFoodSchema(BaseModel):
    """Схема запроса блюд"""

    ids: Optional[List[int]] = (None,)
    is_published: Optional[bool] = (None,)
    is_vegan: Optional[bool] = (None,)
    is_special: Optional[bool] = (None,)
    grouped_by_categories: Optional[bool] = (None,)
    topping_name: Optional[str] = (None,)


class ResponseFoodSchema(BaseFoodSchema):
    """Схема получения блюда"""

    id: int


class SaveFoodSchema(BaseFoodSchema):
    """Схема создания/обновления блюда"""

    id: Optional[int] = None


class DeleteFoodSchema(BaseModel):
    """Схема блюд к удалению"""

    food_ids: List[int]


class DeletedFoodSchema(BaseModel):
    """Схема удаленных блюд"""

    deleted_food_ids: List[int]
