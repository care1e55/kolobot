.PHONY: all build up down clean unit integration test lint unit black ruff quality codebase metadata metadata-test \
metadata-prod health health-test health-prod query query-prod query-test benchmark benchmark-test benchmark-prod
PYTHONPATH := ${PYTHONPATH}:$(pwd)
INSTALL_DEPS_DEV := true
SERVICE_NAME := service
CHECK_PATH := .
.DEFAULT_GOAL := help

# If .env file is found, assign variables from this source (overriding existing)
ifneq (,$(wildcard .env))
    $(info FOUND .env File.)
    include .env
endif

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([\w_-]+):.*?## (.*)$$', line)	
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

api:
	uvicorn src.api:app --port 8040 --host '0.0.0.0'

ui:
	streamlit run src/Welcome.py

build: ## Build image
	docker-compose build --build-arg PYPI_USER=${PYPI_USER} --build-arg PYPI_PASSWORD=${PYPI_PASSWORD} --build-arg INSTALL_DEPS_DEV=${INSTALL_DEPS_DEV}

up: ## Run the service
	docker-compose up -d ${SERVICE_NAME}

down: ## Down the service
	docker-compose down

clean: ## Clean temporary files
	find . \( -name \*.pyc -o -name \.pytest_cache -o -name \.ruff_cache -o -name \__pycache__ \) -exec rm -rf {} +

integration: ## Run integration tests
	docker-compose up --exit-code-from=tests tests

test: ## Run particular tests
	docker-compose run --rm ${SERVICE_NAME} poetry run pytest ${TEST_ARGS} ${TEST_PATH}

lint: black ruff ## Run all code checks

unit: ## Run unit tests
	docker-compose run --rm --no-deps ${SERVICE_NAME} poetry run pytest -m unit

black: ## Check formatting
	docker-compose run --rm --no-deps ${SERVICE_NAME} poetry run black --check ${CHECK_PATH}

ruff: ## Check bugs and code smells
	docker-compose run --rm --no-deps ${SERVICE_NAME} poetry run ruff ${CHECK_PATH}

quality: ## Check quality on the test dataset
	docker-compose run --rm ${SERVICE_NAME} python scripts/check_quality.py ${CHECK_ARGS}

metadata: ## Show metadata of the local service
	curl -XGET 'http://localhost:9000/api/v1.0/metadata' | json_pp -json_opt pretty,canonical

metadata-test: ## Show metadata of the service on the test environment
	curl -XGET 'https://intent-classifier-test.ds.anna.money/api/v1.0/metadata' | json_pp -json_opt pretty,canonical

metadata-prod: ## Show metadata of the service on the production environment
	curl -XGET 'https://intent-classifier-datascience.ds.anna.money/api/v1.0/metadata' | json_pp -json_opt pretty,canonical

health: ## Show the health status of the local service
	curl -XGET 'http://localhost:9000/api/v1.0/health/status' | json_pp -json_opt pretty,canonical

health-test: ## Show the health status of the service on the test environment
	curl -XGET 'https://intent-classifier-test.ds.anna.money/api/v1.0/health/status' | json_pp -json_opt pretty,canonical

health-prod: ## Show the health status of the service on the production environment
	curl -XGET 'https://intent-classifier-datascience.ds.anna.money/api/v1.0/health/status' | json_pp -json_opt pretty,canonical

query: ## Make a query to the local service
	curl -XPOST 'http://localhost:9000/api/v1.0/predictions' \
	--header 'Content-Type: application/json' \
	--data-raw '{"jsonData": {"text": "${TEXT}", "entities": [${ENTITIES}]}}' | json_pp -json_opt pretty,canonical

query-test: ## Make a query to the test environment
	curl -XPOST 'https://intent-classifier-test.ds.anna.money/api/v1.0/predictions' \
	--header 'Content-Type: application/json' \
	--data-raw '{"jsonData": {"text": "${TEXT}", "entities": [${ENTITIES}]}}' | json_pp -json_opt pretty,canonical

query-prod: ## Make a query to the production environment
	curl -XPOST 'https://intent-classifier-datascience.ds.anna.money/api/v1.0/predictions' \
	--header 'Content-Type: application/json' \
	--data-raw '{"jsonData": {"text": "${TEXT}", "entities": [${ENTITIES}]}}' | json_pp -json_opt pretty,canonical

codebase: ## Calculate number of code lines (required cloc to be installed)
	cloc $$(git ls-files)

create-postdata: ## Create a file for bechmarking
	echo {\"jsonData\": {\"text\": \"from new to old\", \"entities\": []}} > postdata.json

benchmark: create-postdata ## Test the local service performance (required ab to be installed)
	ab -T 'application/json' -p postdata.json -c 10 -n 100 http://localhost:9000/api/v1.0/predictions

benchmark-test: create-postdata ## Test the service performance on the test environment (required ab to be installed)
	ab -T 'application/json' -p postdata.json -c 10 -n 100 https://intent-classifier-test.ds.anna.money/api/v1.0/predictions

benchmark-prod: create-postdata ## Test the service performance on the production environment (required ab to be installed)
	ab -T 'application/json' -p postdata.json -c 10 -n 100 https://intent-classifier-datascience.ds.anna.money/api/v1.0/predictions
