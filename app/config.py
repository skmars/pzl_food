from pathlib import Path

from dynaconf import settings as config

PROJECT_PATH = str(Path(__file__).parent.parent.resolve())

settings = config
settings.configure(ENVVAR_PREFIX_FOR_DYNACONF=False)

DB_URL = "postgresql://{username}:{password}@{host}:{port}/{database}".format(
    username=settings.POSTGRES.user,
    password=settings.POSTGRES.password,
    host=settings.POSTGRES.host,
    port=settings.POSTGRES.port,
    database=settings.POSTGRES.database,
)
