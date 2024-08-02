from typing import (
    List,
    Optional,
)

from sqlalchemy import select

from app.core.database import Database
from app.models import (
    Food,
    FoodCategory,
)


async def get_foods_grouped_by_category(
    db: Database,
    ids: Optional[List[int]] = None,
    is_published: Optional[bool] = None,
    is_vegan: Optional[bool] = None,
    is_special: Optional[bool] = None,
    grouped_by_categories: Optional[bool] = None,
    topping_name: Optional[str] = None,
) -> List[Food]:
    """Получение списка блюд относительно категорий"""
    async with db.async_context() as session:
        stmt = select(FoodCategory).outerjoin(Food, Food.category_id == FoodCategory.id)
        if ids:
            stmt = stmt.filter(Food.id.in_(ids))
        if is_published:
            stmt = stmt.filter(Food.is_published is True)
        if is_vegan:
            stmt = stmt.filter(Food.is_vegan is True)
        if is_special:
            stmt = stmt.filter(Food.is_special is True)
        if topping_name:
            stmt = stmt.filter(topping_name in {topping.name for topping in Food.toppings})
        if grouped_by_categories:
            stmt = stmt.group_by(Food.category_id)

        stmt = stmt.order_by(Food.id.desc())
        result = await session.execute(stmt).unique()
        return result.scalars().fetchall()
