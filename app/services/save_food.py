from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Database
from app.models import (
    Food,
    Topping,
    ToppingFoodReference,
)
from app.schemas import SaveFoodSchema
from app.services.utils import update_instance_fields
from app.validation import (
    validate_food_create,
    validate_food_update,
)


async def create_toppings(session: AsyncSession, topping_name: str, food_id: int) -> None:
    """Создание ингридиента"""
    topping = Topping(name=topping_name)
    session.add(topping)
    await session.flush()
    topping_reference = ToppingFoodReference(topping_id=topping.id, food_id=food_id)
    session.add(topping_reference)
    await session.flush()


async def create_food(db: Database, food_data: SaveFoodSchema) -> Food:
    """Создание блюда"""
    async with db.async_context() as session:
        await validate_food_create(session, food_data.id)
        food = food_data.model_dump(exclude={"id", "toppings"})
        food = Food(**food)
        _ = {create_toppings(session, topping_name=t_name, food_id=food.id) for t_name in food_data.toppings}
        session.add(food)
        await session.flush()
    return food


async def update_food(
    db: Database,
    food_data: SaveFoodSchema,
) -> Food:
    """Обновление блюда"""

    async with db.async_context() as session:
        await validate_food_update(session, food_data)
        food = food_data.model_dump(exclude={"id", "toppings"})
        update_instance_fields(food, food_data)
    return food


async def save_foods(
    db: Database,
    data: SaveFoodSchema,
) -> Food:
    """Сохранение блюд"""

    if not data.id:
        food = await create_food(db, data)
    else:
        food = await update_food(db, data)
    return food
