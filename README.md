# E-commerce API

Simple e-commerce backend API built with **FastAPI**, **SQLAlchemy**, **Alembic**, **PostgreSQL**, **Docker Compose**, and **Pytest**.

The project allows managing:

* clients;
* products;
* warehouses;
* stock;
* orders.

## Project structure

```text
.
├── Makefile
├── README.md
├── app
│   ├── Dockerfile
│   ├── Makefile
│   ├── data
│   ├── migrations
│   ├── scripts
│   ├── src
│   └── tests
└── docker
    ├── compose-prod.yml
    ├── compose-test.yml
    └── postgres.conf
```

## Main directories

### `app/src`

Main application source code.

```text
src
├── api
├── config
├── infrastructure
├── main.py
├── models
├── repositories
└── services
```

* `api` — FastAPI routers, schemas, dependencies, middlewares and error handlers.
* `config` — application settings from environment variables.
* `infrastructure` — database engine and session configuration.
* `models` — SQLAlchemy database models.
* `repositories` — database query layer.
* `services` — business logic, for example order creation.
* `main.py` — application entry point.

### `app/migrations`

Alembic migrations for database schema changes.

### `app/tests`

Automated tests for API endpoints and business logic.

### `docker`

Docker Compose files for production-like and test environments.

## How to run docker

Create production `env` file:

```bash
cp docker/.env.example docker/.env
```

Example `docker/.env`:

```env
# Service
SERVICE__NAMESPACE=web-app
SERVICE__NAME=web-app
SERVICE__VERSION=0.1.0
SERVICE__STAGE=local

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_password
POSTGRES_DB=ecommerce
POSTGRES_PORT=5432

# PgBouncer
PGBOUNCER_PORT=5433
```

Start the project:

```bash
make prod
```

Open API documentation:

```text
http://localhost:8000/docs
```

## How to run tests

Create test `.env.test` file or you can use ready files

```bash
touch docker/.env.test
```

Example `docker/.env.test`:

```env
# Service
SERVICE__NAMESPACE=test-web-app
SERVICE__NAME=test-web-app
SERVICE__VERSION=0.1.0
SERVICE__STAGE=test

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_password
POSTGRES_DB=ecommerce_test
POSTGRES_PORT=5432
```

```bash
touch app/.env.test
```

Example `app/.env.test`:

```env
# App
DEBUG=True

# Service
SERVICE__NAMESPACE=web-app
SERVICE__NAME=web-app
SERVICE__VERSION=0.1.0
SERVICE__STAGE=local

# Database via PgBouncer
DATABASE__URI=postgresql+asyncpg://postgres:postgres_password@localhost:5432/ecommerce_test
DATABASE__POOL_SIZE=30
DATABASE__MAX_OVERFLOW=15
DATABASE__POOL_TIMEOUT=120
DATABASE__POOL_RECYCLE=900
```

Run tests:

```bash
make test
```

This command starts the test database, waits until it is ready, runs tests with coverage, and then stops the test environment.

## Useful commands

```bash
make prod          # start production-like environment
make test          # run tests with Docker test database
prod-clear         # down docker compose
```


## How to run local

```bash
docker compose --env-file docker/.env -f docker/compose-prod.yml up -d db
```

```bash
cp app/.env.example app/.env
```

Example `app/.env`:

```env
# App
DEBUG=True

# Service
SERVICE__NAMESPACE=web-app
SERVICE__NAME=web-app
SERVICE__VERSION=0.1.0
SERVICE__STAGE=local

# Database via PgBouncer
DATABASE__URI=postgresql+asyncpg://postgres:postgres_password@localhost:5432/ecommerce
DATABASE__POOL_SIZE=30
DATABASE__MAX_OVERFLOW=15
DATABASE__POOL_TIMEOUT=120
DATABASE__POOL_RECYCLE=900
```

```bash
cd ./app
make start-api-dev
```



## Architecture

The project uses a layered structure:

```text
router -> service -> repository -> database
```

Routers handle HTTP requests and responses.
Repositories contain database queries.
Services contain business logic, such as creating orders, checking stock availability, and calculating totals.
This approach keeps the code easier to test, maintain, and extend.

