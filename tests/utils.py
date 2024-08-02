import os
import uuid
from argparse import Namespace
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import (
    AsyncIterator,
    Optional,
    Union,
)

from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils.functions.database import (
    _set_url_database,
    make_url,
)
from sqlalchemy_utils.functions.orm import quote

from app import __name__ as project_name


async def create_database_async(db_url: str, encoding: str = "utf8", template: Optional[str] = None) -> None:
    url = make_url(db_url)
    database = url.database

    url = _set_url_database(url, database="postgres")
    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    if not template:
        template = "template1"

    async with engine.begin() as conn:
        stmt = f"CREATE DATABASE {quote(conn, database)} ENCODING '{encoding}' TEMPLATE {quote(conn, template)}"
        await conn.execute(text(stmt))

    await engine.dispose()


async def drop_database_async(db_url: str) -> None:
    url = make_url(db_url)
    database = url.database

    url = _set_url_database(url, database="postgres")
    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    async with engine.begin() as conn:
        # Disconnect all users from the database we are dropping.
        version = conn.dialect.server_version_info
        pid_column = "pid" if (version >= (9, 2)) else "procpid"
        stmt = """
            SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}'
            AND {pid_column} <> pg_backend_pid();
        """.format(
            pid_column=pid_column, database=database
        )
        await conn.execute(text(stmt))

        # Drop the database.
        stmt = f"DROP DATABASE {quote(conn, database)}"
        await conn.execute(text(stmt))

    await engine.dispose()


@asynccontextmanager
async def tmp_database(db_url: URL, suffix: str = "", **kwargs) -> AsyncIterator[str]:
    """
    Контекстный менеджер для создания тестовой БД и последующего удаления
    """
    tmp_db_name = ".".join([uuid.uuid4().hex, project_name, suffix])
    tmp_db_url = str(db_url.with_path(tmp_db_name))
    await create_database_async(tmp_db_url, **kwargs)
    try:
        yield tmp_db_url
    finally:
        await drop_database_async(tmp_db_url)


def make_alembic_config(cmd_opts: Union[Namespace, SimpleNamespace]) -> Config:
    """
    Создаем конфигурационный файл Алембика
    """
    base_path = str(Path(__file__).parent.parent.resolve())
    # Replace path to alembic.ini file to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)
    config.set_main_option("script_location", os.path.join(base_path, "db", "alembic"))
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_url)

    return config


def alembic_config_from_url(pg_url: Optional[str] = None) -> Config:
    """
    Объект-имитация данных для alembic.ini
    """
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        pg_url=pg_url,
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_options)
