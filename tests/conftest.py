import asyncio
from typing import Optional
from unittest.mock import (
    AsyncMock,
    Mock,
)

import pytest
from alembic.command import upgrade
from fastapi import FastAPI
from fastapi.testclient import TestClient
from yarl import URL

from app.api.routers import health_check
from app.config import settings
from app.core.context import ApplicationContext
from app.core.database import (
    Database,
    get_db_url,
)
from app.models import (
    Food,
    FoodCategory,
    Topping,
    ToppingFoodReference,
)
from tests.utils import (
    alembic_config_from_url,
    tmp_database,
)

MIGRATION_TASK: Optional[asyncio.Task] = None


@pytest.fixture(scope="session")
def pg_url() -> str:
    """
    Provides base PostgreSQL URL for creating temporary databases.
    """

    return URL(get_db_url(settings.POSTGRES))


@pytest.fixture
async def empty_temp_db(pg_url):
    """
    Создаем пустую временную БД для теста миграций
    """

    async with tmp_database(db_url=pg_url, suffix="pytest_migration") as tmp_url:
        yield tmp_url


@pytest.fixture
def test_db_alembic_config(empty_temp_db):
    """
    Связываем конфигурационный файл alembic с пустой временной БД
    """

    return alembic_config_from_url(pg_url=empty_temp_db)


@pytest.fixture(scope="session")
async def migrated_postgres_template(pg_url):
    """
    Creates temporary database and applies migrations.
    Has "session" scope, so is called only once per tests run.
    """

    async with tmp_database(pg_url, "migrated_template") as tmp_url:
        alembic_config = alembic_config_from_url(tmp_url)
        upgrade(alembic_config, "head")
        await MIGRATION_TASK
        yield tmp_url


@pytest.fixture
async def migrated_temp_db(pg_url, migrated_postgres_template):
    """
    Copy a clean database with migrations using a database template.
    The fixture is used for tests where a clean database with migrations is needed.
    """

    template_db_name = URL(migrated_postgres_template).name
    async with tmp_database(db_url=pg_url, suffix="pytest_db", template=template_db_name) as tmp_url:
        yield tmp_url


@pytest.fixture
def request_context():
    yield Mock()


@pytest.fixture
async def db_context(migrated_temp_db):
    database = Database(settings.POSTGRES, db_url=migrated_temp_db)
    database.connect()
    yield database
    await database.close()


@pytest.fixture
def client_context(
    request_context,
    db_context,
) -> ApplicationContext:
    return ApplicationContext(
        request=request_context,
        database=db_context,
    )


@pytest.fixture
def rest_client(client_context):
    app = FastAPI()
    app.extra["context"] = client_context
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture
def make_food_category(db_context):
    async def create_food_category(**kwargs):
        async with db_context.async_session() as session:
            food_category = FoodCategory(
                name=kwargs.get("name", "Выпечка"),
                is_published=kwargs.get("is_published", True),
            )
            session.add(food_category)
            return food_category

    return create_food_category


@pytest.fixture
def make_toppings(db_context):
    async def create_topping(**kwargs):
        async with db_context.async_session() as session:
            topping = Topping(
                name=kwargs.get("name", "Перо динозавра"),
            )
            session.add(topping)
            return topping

    return create_topping


@pytest.fixture
def make_topping_food_references(db_context):
    async def create_topping_food_reference(**kwargs):
        async with db_context.async_session() as session:
            topping_food_reference = ToppingFoodReference(
                topping_id=kwargs.get("topping_id"),
                food_id=kwargs.get(
                    "food_id",
                ),
            )
            session.add(topping_food_reference)
            return topping_food_reference

    return create_topping_food_reference


@pytest.fixture
def make_foods(db_context):
    async def create_food(**kwargs):
        async with db_context.async_session() as session:
            food = Food(
                description=kwargs.get("description", "Что-то особенное"),
                price=kwargs.get("price", 339),
                is_special=kwargs.get("is_special", True),
                is_vegan=kwargs.get("is_vegan", True),
                is_published=kwargs.get("is_published", True),
                category_id=kwargs.get("category_id"),
            )
            toppings = kwargs.get("toppings")
            if not toppings:
                _ = {make_toppings() for _ in range(5)}
            else:
                _ = {make_toppings(name=topping_name) for topping_name in toppings}
            _ = {make_topping_food_references({"topping_id": topping.id, "food_id": food.id}) for topping in toppings}

            session.add(food)
            return food

    return create_food
