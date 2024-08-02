#!make
# Setup the shell and python version.
# It's necessary to set this because some environments don't link sh -> bash.
SHELL := /bin/bash
PYTHON := python3
SERVICES := app

DB_HOST := $(shell python -c 'from app.config import settings; print(settings.POSTGRES.host)')
DB_PORT := $(shell python -c 'from app.config import settings; print(settings.POSTGRES.port)')
DB_USER := $(shell python -c 'from app.config import settings; print(settings.POSTGRES.user)')
DB_NAME := $(shell python -c 'from app.config import settings; print(settings.POSTGRES.database)')
PG_PASSWORD := $(shell python -c 'from app.config import settings; print(settings.POSTGRES.password)')

.PHONY: help venv install sort lint black test cover migrations migrate create_db backup_db drop_db clean

help:
	@echo "Использование: make <command>"
	@echo
	@echo "Доступные команды:"
	@echo "  venv               Создание виртуального окружения"
	@echo "  install            Установка зависимостей"
	@echo "  sort               Сортировка импортов"
	@echo "  lint               Запуск линтеров"
	@echo "  black              Запуск форматтера black"
	@echo "  test               Запуск тестов"
	@echo "  cover              Запуск вычисления покрытия тестов"
	@echo "  migrations         Создание и добавление в индекс файла миграции"
	@echo "  migrate            Обновление миграций базы данных"
	@echo "  create_db          Создание базы данных"
	@echo "  backup_db          Создание бэкапа базы данных"
	@echo "  drop_db            Удаление базы данных"

venv:
	$(PYTHON) -m venv .venv
	@echo "Для активации venv используйте 'source .venv/bin/activate'"

install:
	@poetry install
	@make lfs
	@git-lfs pull

sort:
	@isort .

lint:
	@flake8 --max-line-length 120 $(SERVICES)
	@pylint $(SERVICES)

black:
	@black .

test:
	@ENV_FOR_DYNACONF=testing pytest tests

cover:
	@ENV_FOR_DYNACONF=testing coverage run --concurrency=thread,greenlet --source=. -m pytest tests
	@coverage report

migrations:
	@alembic revision --autogenerate -m "auto"
	@git add db/alembic/versions/.

migrate:
	@alembic upgrade head

create_db:
	@psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -w "${PG_PASSWORD}" -c "CREATE DATABASE ${DB_NAME}"

backup_db:
	@psql -h ${DB_HOST}	-p ${DB_PORT} -U "${DB_USER}" -w ${PG_PASSWORD} -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '${DB_NAME}' AND pid <> pg_backend_pid();"
	@psql -h "${DB_HOST}" -p ${DB_PORT} -U "${DB_USER}" -w ${PG_PASSWORD} -c "ALTER DATABASE ${DB_NAME} RENAME TO ${DB_NAME}_$(date +%s);"

drop_db:
	@psql -h ${DB_HOST}	-p ${DB_PORT} -U "${DB_USER}" -w ${PG_PASSWORD} -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '${DB_NAME}' AND pid <> pg_backend_pid();"
	@psql -h "${DB_HOST}" -p ${DB_PORT} -U "${DB_USER}" -w ${PG_PASSWORD} -c "DROP DATABASE IF EXISTS ${DB_NAME};"


