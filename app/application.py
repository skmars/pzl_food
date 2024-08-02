from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import food
from app.config import settings
from app.core.context import ApplicationContext
from app.core.database import Database


class Application:
    def __init__(self) -> None:
        self.app = FastAPI(debug=settings.DEBUG, lifespan=self.lifespan)
        self.settings = settings
        self.database = Database(settings.POSTGRES)
        self.context = self.init_context()

    @asynccontextmanager
    async def lifespan(self, _):
        self.database.connect()
        yield
        await self.database.close()

    def init_context(self) -> ApplicationContext:
        """
        Инициализация контекста сервиса
        """

        # pylint: disable=unexpected-keyword-arg
        return ApplicationContext(
            database=self.database,
        )

    def add_routers(self) -> None:
        """
        Добавление роутеров
        """

        self.app.include_router(food.router)

    def init_app(self) -> FastAPI:
        """
        Инициализация зависимостей
        """

        self.add_routers()
        self.app.extra["context"] = self.context
        return self.app


app = Application().init_app()
