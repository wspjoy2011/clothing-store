ENV_FILE=services/backend/.env

.PHONY: help up down build logs restart

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

down:  ## Stop all services
	docker compose --env-file $(ENV_FILE) down

logs:  ## Show container logs
	docker compose --env-file $(ENV_FILE) logs -f

restart:  ## Restart services (down, build, up)
	make down && make build && make up
