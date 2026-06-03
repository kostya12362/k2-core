ENV_FILE = docker/.env.test
COMPOSE_TEST = docker compose --env-file $(ENV_FILE) -f docker/compose-test.yml
APP_DIR = app
DB_SERVICE = test-db

.PHONY: help \
	test test-up test-down test-restart test-logs test-ps \
	test-cov test-unit test-shell test-db-shell wait-test-db clean-test

help:
	@echo "Available commands:"
	@echo "  make test           - Start test compose, run coverage tests, stop compose"
	@echo "  make test-up        - Start test compose with .env.test"
	@echo "  make test-down      - Stop test compose and remove volumes"
	@echo "  make test-restart   - Restart test compose"
	@echo "  make test-logs      - Show test compose logs"
	@echo "  make test-ps        - Show test compose containers"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make test-unit      - Run tests without coverage"
	@echo "  make test-shell     - Open app shell"
	@echo "  make test-db-shell  - Open test database shell"
	@echo "  make clean-test     - Stop compose, remove volumes and orphan containers"

test:
	$(COMPOSE_TEST) up -d
	$(MAKE) wait-test-db
	cd $(APP_DIR) && set -a && . .env.test && set +a && make test-cov; \
	status=$$?; \
	cd ..; \
	$(COMPOSE_TEST) down -v; \
	exit $$status

test-down:
	$(COMPOSE_TEST) down -v

prod:
	docker compose --env-file docker/.env -f docker/compose-prod.yml up -d --build

prod-clear:
	docker compose --env-file docker/.env -f docker/compose-prod.yml down -v