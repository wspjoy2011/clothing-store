
ENV_FILE=services/backend/.env

.PHONY: help up down build logs restart sync-products migrate-status migrate-up migrate-dry-run migrate-force rollback-last rollback-dry-run rollback-force rollback-to

## Show this help
help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
		sed -E 's/^[a-zA-Z_-]+:.*?## //g' | \
		paste -d ':' - <(grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sed -E 's/:.*//') | \
		awk -F ':' '{printf "  \033[36m%-25s\033[0m %s\n", $$2, $$1}'

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

# ============================================
# Migration Commands
# ============================================

migrate-status: ## Show database migration status
	@echo "========================================="
	@echo "Database Migration Status"
	@echo "========================================="
	@echo "Starting database..."
	docker compose --env-file $(ENV_FILE) up -d db
	@echo "Waiting for database to be ready (15s)..."
	@sleep 15
	@echo "Checking migration status..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm backend-runner python -m migrations.cli status
	@echo "Stopping database..."
	docker compose --env-file $(ENV_FILE) stop db
	@echo "========================================="
	@echo "Migration status check completed!"
	@echo "========================================="

migrate-up: ## Apply pending database migrations (with confirmation)
	@echo "========================================="
	@echo "Database Migration - Apply Pending"
	@echo "========================================="
	@echo "Starting database..."
	docker compose --env-file $(ENV_FILE) up -d db
	@echo "Waiting for database to be ready (15s)..."
	@sleep 15
	@echo "Applying pending migrations (interactive)..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm -it backend-runner python -m migrations.cli migrate
	@echo "Stopping database..."
	docker compose --env-file $(ENV_FILE) stop db
	@echo "========================================="
	@echo "Database migration completed!"
	@echo "========================================="

migrate-dry-run: ## Show what migrations would be applied (dry run)
	@echo "========================================="
	@echo "Database Migration - Dry Run"
	@echo "========================================="
	@echo "Starting database..."
	docker compose --env-file $(ENV_FILE) up -d db
	@echo "Waiting for database to be ready (15s)..."
	@sleep 15
	@echo "Running migration dry-run..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm backend-runner python -m migrations.cli migrate --dry-run
	@echo "Stopping database..."
	docker compose --env-file $(ENV_FILE) stop db
	@echo "========================================="
	@echo "Migration dry run completed!"
	@echo "========================================="

migrate-force: ## Apply pending migrations without confirmation
	@echo "========================================="
	@echo "Database Migration - Force Apply"
	@echo "========================================="
	@echo "Starting database..."
	docker compose --env-file $(ENV_FILE) up -d db
	@echo "Waiting for database to be ready (15s)..."
	@sleep 15
	@echo "Applying migrations (force mode)..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm backend-runner python -m migrations.cli migrate --force
	@echo "Stopping database..."
	docker compose --env-file $(ENV_FILE) stop db
	@echo "========================================="
	@echo "Migration completed!"
	@echo "========================================="

# ============================================
# Rollback Commands
# ============================================

rollback-last: ## Rollback the last applied migration (with confirmation)
	@echo "========================================="
	@echo "Database Rollback - Last Migration"
	@echo "========================================="
	@echo "Starting database..."
	docker compose --env-file $(ENV_FILE) up -d db
	@echo "Waiting for database to be ready (15s)..."
	@sleep 15
	@echo "Rolling back last migration (interactive)..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm -it backend-runner python -m migrations.cli rollback
	@echo "Stopping database..."
	docker compose --env-file $(ENV_FILE) stop db
	@echo "========================================="
	@echo "Database rollback completed!"
	@echo "========================================="

rollback-dry-run: ## Show what would be rolled back (dry run)
	@echo "========================================="
	@echo "Database Rollback - Dry Run"
	@echo "========================================="
	@echo "Starting database..."
	docker compose --env-file $(ENV_FILE) up -d db
	@echo "Waiting for database to be ready (15s)..."
	@sleep 15
	@echo "Running rollback dry-run..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm backend-runner python -m migrations.cli rollback --dry-run
	@echo "Stopping database..."
	docker compose --env-file $(ENV_FILE) stop db
	@echo "========================================="
	@echo "Rollback dry run completed!"
	@echo "========================================="

rollback-force: ## Rollback last migration without confirmation
	@echo "========================================="
	@echo "Database Rollback - Force"
	@echo "========================================="
	@echo "Starting database..."
	docker compose --env-file $(ENV_FILE) up -d db
	@echo "Waiting for database to be ready (15s)..."
	@sleep 15
	@echo "Rolling back last migration (force mode)..."
	docker compose --env-file $(ENV_FILE) --profile tools run --rm backend-runner python -m migrations.cli rollback --force
	@echo "Stopping database..."
	docker compose --env-file $(ENV_FILE) stop db
	@echo "========================================="
	@echo "Rollback completed!"
	@echo "========================================="

rollback-to: ## Rollback to specific version (interactive)
	@echo "========================================="
	@echo "Database Rollback - To Version"
	@echo "========================================="
	@read -p "Enter target version to rollback to: " VERSION; \
	if [ -z "$$VERSION" ]; then \
		echo "Version is required. Operation cancelled."; \
		exit 1; \
	fi; \
	echo "Starting database..."; \
	docker compose --env-file $(ENV_FILE) up -d db; \
	echo "Waiting for database to be ready (15s)..."; \
	sleep 15; \
	echo "Rolling back to version $$VERSION (interactive)..."; \
	docker compose --env-file $(ENV_FILE) --profile tools run --rm -it backend-runner python -m migrations.cli rollback --to-version $$VERSION; \
	echo "Stopping database..."; \
	docker compose --env-file $(ENV_FILE) stop db; \
	echo "========================================"; \
	echo "Rollback completed!"; \
	echo "========================================"

# ============================================
# Product Sync Commands
# ============================================

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

# ============================================
# Service Management
# ============================================

down:  ## Stop all services
	docker compose --env-file $(ENV_FILE) down

logs:  ## Show container logs
	docker compose --env-file $(ENV_FILE) logs -f

restart:  ## Restart services (down, build, up)
	make down && make build && make up
