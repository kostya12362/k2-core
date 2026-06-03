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
	@echo "  make test-down      - Stop test compose and remove volumes"
	@echo "  make prod			 - Run prod compose"
	@echo "  prod-clear		     - Clear prod "
test:
	$(COMPOSE_TEST) up -d
	$(MAKE) wait-test-db
	cd $(APP_DIR) && set -a && . ../$(ENV_FILE) && set +a && make test-cov; \
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