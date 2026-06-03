.PHONY: setup start-api-dev start-api-prod init-migrations makemigrations migrate lint test test-cov test-cov-html
export PYTHONPATH := src

ifneq (,$(wildcard .env))
    include .env
    export
endif

setup:
	poetry install


start-api-dev:
	poetry run alembic -c migrations/alembic.ini upgrade head
	poetry run uvicorn main:app --host 0.0.0.0 --port 8001 --reload

start-api-prod:
	poetry run alembic -c migrations/alembic.ini upgrade head
	poetry run uvicorn main:app --host 0.0.0.0 --port 8001 --workers 5

test:
	poetry run pytest -v

test-cov:
	poetry run pytest -v --cov=src --cov-report=term-missing

test-cov-html:
	poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=html

init-migrations:
	poetry run alembic -c migrations/alembic.ini init -t async migrations

makemigrations:
	poetry run alembic -c migrations/alembic.ini revision --autogenerate

migrate:
	poetry run alembic -c migrations/alembic.ini upgrade head

lint:
	poetry run ruff check src/ --fix
	poetry run ruff format src/