from typing import (
    List,
    Set,
)

from sqlalchemy import select

from app.core.database import Database
from app.models import Food
from app.services.utils import delete_instances


async def delete_foods(
    db: Database,
    ids_to_delete: List[int],
) -> Set[int]:
    async with db.async_context() as session:
        instances_to_delete = (
            (await session.execute(select(Food).where(Food.id.in_(ids_to_delete)))).scalars().fetchall()
        )
        persistent_food_ids = {instance.id for instance in instances_to_delete}
        delete_instances(session, persistent_food_ids, Food)

        return persistent_food_ids
