from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.models import BaseModel


class FoodCategory(BaseModel):
    """Категория блюда"""

    __tablename__ = "food_category"
    __table_args__ = {"comment": __doc__}

    id = Column(Integer, primary_key=True, doc="Внутренний идентификатор")
    name = Column(String, nullable=False, comment="Наименование")
    is_published = Column(Boolean, nullable=False, default=True, comment="Признак заявленной категории")
    foods = relationship(
        "Food",
        doc="Блюда",
        lazy="joined",
        order_by="Food.id",
        back_populates="food",
    )


class Food(BaseModel):
    """Блюдо"""

    __tablename__ = "food"
    __table_args__ = {"comment": __doc__}

    id = Column(Integer, primary_key=True, doc="Внутренний идентификатор")
    description = Column(String, nullable=False, comment="Описание")
    price = Column(Integer, nullable=False, comment="Цена")
    is_special = Column(Boolean, nullable=False, default=False, comment="Признак специального блюда")
    is_vegan = Column(Boolean, nullable=False, default=False, comment="Признак вегатерианского блюда")
    is_published = Column(Boolean, nullable=False, default=True, comment="Признак заявленного блюда")
    category_id = Column(
        Integer,
        ForeignKey("food_category.id", ondelete="CASCADE"),
        nullable=True,
        doc="Идентификатор категории блюда",
    )
    toppings = relationship(
        "ToppingFoodReference",
        doc="Ингредиенты блюда",
        lazy="selectin",
        secondary="topping__food__reference",
        order_by="Topping.id",
    )
