from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Food
from app.services.utils import fetch_instance


async def validate_food_create(session: AsyncSession, food_id: int) -> None:
    if await fetch_instance(session, Food, food_id):
        raise HTTPException(
            status_code=422,
            detail=("Такое блюдо уже есть: %s!", food_id),
        )


async def validate_food_update(session: AsyncSession, food_id: int) -> Food:
    if not await fetch_instance(session, Food, food_id):
        raise HTTPException(
            status_code=422,
            detail=("Такого блюда не существует: %s!", food_id),
        )
