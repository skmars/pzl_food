from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)

from app.models import (
    Base,
    BaseModel,
)


class Topping(BaseModel):
    """Ингредиент"""

    __tablename__ = "topping"
    __table_args__ = {"comment": __doc__}

    id = Column(Integer, primary_key=True, doc="Внутренний идентификатор")
    name = Column(String, nullable=False, comment="Наименование")


class ToppingFoodReference(Base):
    """
    Таблица m2m для связи ингредиентов и блюд
    """

    __tablename__ = "topping__food__reference"
    __table_args__ = {"comment": __doc__}

    topping_id = Column(
        Integer,
        ForeignKey("topping.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Идентификатор ингредиента",
    )
    food_id = Column(Integer, ForeignKey("food.id"), primary_key=True, doc="Идентификатор блюда")
