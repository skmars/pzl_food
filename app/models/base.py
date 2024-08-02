from datetime import (
    datetime,
    timezone,
)
from functools import partial

from sqlalchemy import (
    Column,
    DateTime,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    uuid = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("uuid_generate_v4()"),
        nullable=False,
        unique=True,
        doc="Уникальный идентификатор объекта",
        comment="Уникальный идентификатор объекта",
    )
    date_created = Column(
        DateTime(timezone=True),
        nullable=False,
        default=partial(datetime.now, timezone.utc),
        doc="Дата создания",
        comment="Дата создания",
    )
    date_updated = Column(
        DateTime(timezone=True),
        nullable=False,
        default=partial(datetime.now, timezone.utc),
        onupdate=datetime.now(timezone.utc).astimezone,
        doc="Дата редактирования",
        comment="Дата редактирования",
    )
    date_deleted = Column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="Дата удаления",
        comment="Дата удаления",
    )
