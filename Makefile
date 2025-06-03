ENV_FILE=services/backend/.env

.PHONY: help up down build logs restart sync-products

## Show this help
help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
		sed -E 's/^[a-zA-Z_-]+:.*?## //g' | \
		paste -d ':' - <(grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sed -E 's/:.*//') | \
		awk -F ':' '{printf "  \033[36m%-15s\033[0m %s\n", $$2, $$1}'


build:  ## Build docker containers
	docker compose --env-file $(ENV_FILE) build

up:  ## Start all services
	docker compose --env-file $(ENV_FILE) up

up-detached:  ## Start all services in detached mode
	docker compose --env-file $(ENV_FILE) up -d

seed-db: ## Start services, run seed.py, then stop services
	docker compose --env-file $(ENV_FILE) up -d db web
	@echo "Waiting for the database to be ready..."
	docker compose --env-file $(ENV_FILE) run --rm web python /usr/src/clothing-store/backend/etl/seed.py
	docker compose --env-file $(ENV_FILE) down

sync-products: ## Synchronize products from PostgreSQL to Elasticsearch
	@echo "========================================="
	@echo "Starting Product Synchronization"
	@echo "========================================="
	@echo "Starting required services: PostgreSQL, Elasticsearch..."
	docker compose --env-file $(ENV_FILE) up -d db elasticsearch
	@echo "Waiting for services to be ready (30s)..."
	@sleep 30
	@echo "Running product synchronization with backend-runner..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm backend-runner python -m etl.commands.sync_products --force
	@echo "Stopping services..."
	docker compose --env-file $(ENV_FILE) stop db elasticsearch
	@echo "========================================="
	@echo "Product synchronization completed!"
	@echo "========================================="

sync-products-dry-run: ## Run product synchronization in dry-run mode (no actual changes)
	@echo "========================================="
	@echo "Starting Product Synchronization (DRY RUN)"
	@echo "========================================="
	docker compose --env-file $(ENV_FILE) up -d db elasticsearch
	@echo "Waiting for services to be ready (30s)..."
	@sleep 30
	@echo "Running product synchronization (dry-run)..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm backend-runner python -m etl.commands.sync_products --dry-run
	@echo "Stopping services..."
	docker compose --env-file $(ENV_FILE) stop db elasticsearch
	@echo "========================================="
	@echo "Dry run completed!"
	@echo "========================================="

sync-products-interactive: ## Run product synchronization with confirmation prompt
	@echo "========================================="
	@echo "Starting Product Synchronization (Interactive)"
	@echo "========================================="
	docker compose --env-file $(ENV_FILE) up -d db elasticsearch
	@echo "Waiting for services to be ready (30s)..."
	@sleep 30
	@echo "Running product synchronization (interactive mode)..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm -it backend-runner python -m etl.commands.sync_products
	@echo "Stopping services..."
	docker compose --env-file $(ENV_FILE) stop db elasticsearch
	@echo "========================================="
	@echo "Product synchronization completed!"
	@echo "========================================="

sync-products-custom: ## Run product synchronization with custom batch size
	@echo "========================================="
	@echo "Starting Product Synchronization (Custom)"
	@echo "========================================="
	@read -p "Enter batch size (default 1000): " BATCH_SIZE; \
	BATCH_SIZE=$${BATCH_SIZE:-1000}; \
	echo "Using batch size: $$BATCH_SIZE"; \
	docker compose --env-file $(ENV_FILE) up -d db elasticsearch; \
	echo "Waiting for services to be ready (30s)..."; \
	sleep 30; \
	echo "Running product synchronization with batch size $$BATCH_SIZE..."; \
	docker compose --env-file $(ENV_FILE) --profile tools run --rm backend-runner python -m etl.commands.sync_products --batch-size $$BATCH_SIZE --force; \
	echo "Stopping services..."; \
	docker compose --env-file $(ENV_FILE) stop db elasticsearch; \
	echo "========================================="; \
	echo "Product synchronization completed!"; \
	echo "========================================="

down:  ## Stop all services
	docker compose --env-file $(ENV_FILE) down

logs:  ## Show container logs
	docker compose --env-file $(ENV_FILE) logs -f

restart:  ## Restart services (down, build, up)
	make down && make build && make up
