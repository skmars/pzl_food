from dataclasses import dataclass
from typing import (
    Any,
    Optional,
)

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.database import Database


@dataclass
class BaseContext:
    database: Optional[Database] = None
    settings: Optional[Any] = None


@dataclass
class ApplicationContext(BaseContext):
    """
    Контекст сервиса
    """


@dataclass
class RequestContext:
    app_context: BaseContext
    request: Request
    session: Optional[AsyncSession] = None
