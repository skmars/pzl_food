import logging
from contextlib import asynccontextmanager
from typing import (
    Any,
    Dict,
    Optional,
)

from dynaconf.utils.boxing import DynaBox
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_engine_from_config,
)
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def get_db_url(settings: DynaBox) -> str:
    return (
        f"{settings.driver}://{settings.user}:{settings.password}@{settings.host}:{settings.port}/{settings.database}"
    )


def create_async_engine(
    settings: DynaBox,
    db_url: Optional[str] = None,
    configuration: Optional[Dict[str, Any]] = None,
) -> AsyncEngine:
    if not configuration:
        async_engine = _create_async_engine(
            url=db_url or get_db_url(settings),
            echo=settings.echo,
            future=True,
            pool_pre_ping=settings.pool_pre_ping,
            pool_recycle=settings.pool_recycle,
        )
    else:
        async_engine = async_engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=NullPool,
        )
    return async_engine


class Database:
    def __init__(self, settings: DynaBox, db_url: Optional[str] = None) -> None:
        self.settings = settings
        self.db_url = db_url
        self._async_engine = None
        self._async_session = None

    def connect(self) -> None:
        """
        Инициализация подключения к базе данных
        """

        logging.info("Инициализировано подключение к базе данных")
        self._async_engine = create_async_engine(self.settings, db_url=self.db_url)
        self._async_session = sessionmaker(
            self._async_engine,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def async_session(self):
        """
        Контекстный менеджер сессии
        """

        async_session = self._async_session()
        try:
            yield async_session
            await async_session.commit()
        except Exception as exc:
            await async_session.rollback()
            logging.exception("Ошибка сессии: %s", str(exc))
            raise exc
        finally:
            await async_session.close()

    @asynccontextmanager
    async def transaction(self):
        """
        Контекстный менеджер транзакции
        """

        async_session = self._async_session()
        try:
            yield async_session.begin()
            await async_session.commit()
        except Exception as exc:
            await async_session.rollback()
            exc_msg = f"Ошибка транзакции: {str(exc)}"
            logging.exception(exc_msg)
            raise DatabaseException(exc_msg) from exc
        finally:
            await async_session.close()

    async def close(self) -> None:
        """
        Закрытие подключения к базе данных
        """

        logging.info("Закрытие подключения к базе данных")
        if self._async_engine:
            await self._async_engine.dispose()


class DatabaseException(Exception):
    pass
