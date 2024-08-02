import asyncio
import sys
from contextvars import ContextVar
from logging.config import fileConfig
from pathlib import Path
from typing import (
    Any,
    Dict,
)

from alembic import context
from alembic.environment import EnvironmentContext
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import DB_URL
from app.models import BaseModel

# fix путей к пакету
MODEL_PATH = str(Path.cwd())
sys.path.append(MODEL_PATH)
# from config import settings  # noqa: I001, E402 isort:skip

ctx_var: ContextVar[Dict[str, Any]] = ContextVar("ctx_var")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# sqlalchemy.url = postgresql://user:pass@localhost/dbname
# Проверяем передан ли нам URL бд для миграций
try:
    pg_url = config.cmd_opts.pg_url
except AttributeError:
    pg_url = None
# Задаем дефолтный URL БД, если явно не передан
if not pg_url:
    config.set_main_option("sqlalchemy.url", DB_URL)

# Таблицы, которые не нужно учитывать при генерации миграций
exclude_tables = config.get_section("alembic:exclude").get("tables", "").split(",")


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in exclude_tables:
        return False
    else:
        return True


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    try:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()
    except AttributeError:
        context_data = ctx_var.get()
        with EnvironmentContext(
            config=context_data["config"],
            script=context_data["script"],
            **context_data["opts"],
        ):
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_object=include_object,
            )
            with context.begin_transaction():
                context.run_migrations()


async def run_async_migrations() -> None:
    """
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connectable = create_async_engine(
        DB_URL,
        configuration=config.get_section(config.config_ini_section, {}),
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    """

    try:
        _ = asyncio.get_running_loop()
    except RuntimeError:
        # there is no loop, can use asyncio.run
        asyncio.run(run_async_migrations())
        return

    from tests import conftest

    ctx_var.set(
        {
            "config": context.config,
            "script": context.script,
            "opts": context._proxy.context_opts,  # type: ignore
        }
    )
    conftest.MIGRATION_TASK = asyncio.create_task(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
