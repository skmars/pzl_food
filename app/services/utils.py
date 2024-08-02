from typing import (
    Any,
    List,
    Optional,
    Set,
    Union,
)

from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import ColumnProperty

from app.models import (
    Base,
    BaseModel,
)


async def fetch_instance(session: AsyncSession, model: Base, instance_id: int) -> Any:
    return (await session.execute(select(model).where(model.id == instance_id))).unique().scalar_one_or_none()


def update_instance_fields(instance, new_fields: Union[dict, BaseModel]) -> dict:
    updated_fields = {}
    model = type(instance)
    if isinstance(new_fields, BaseModel):
        new_fields = new_fields.model_dump()
    for attribute, new_value in new_fields.items():
        model_field = model.__dict__.get(attribute)
        if model_field and isinstance(model_field.property, ColumnProperty):
            if getattr(instance, attribute) != new_value:
                setattr(instance, attribute, new_value)
                updated_fields[attribute] = new_value

    return updated_fields


async def delete_instances(
    session: AsyncSession, instance_ids: Union[List[int], Set[int]], model: Base, attribute: Optional[str] = "id"
) -> None:
    if instance_ids:
        await session.execute(delete(model).where(getattr(model, attribute).in_(instance_ids)))
