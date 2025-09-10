# Makefile for Power Tariffs PostgreSQL Docker Compose Management

# Variables
COMPOSE_FILE := docker-compose.yaml
DB_CONTAINER := power-tariffs-db
DB_NAME := power-tariffs
DB_USER := power-tariffs
DB_PASSWORD := password
DB_PORT := 5435

# Default target
.DEFAULT_GOAL := help

# Help command
.PHONY: help
help: ## Show this help message
	@echo "Power Tariffs PostgreSQL Docker Management"
	@echo "========================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make up              - Start all services in the background"
	@echo "  make down            - Stop and remove all containers"
	@echo "  make start           - Start existing containers"
	@echo "  make stop            - Stop running containers without removing them"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - Show logs for all services"
	@echo "  make logs-db         - Show logs for PostgreSQL only"
	@echo "  make ps              - Show status of all containers"
	@echo ""
	@echo "Database Management:"
	@echo "  make db-shell        - Connect to PostgreSQL shell"
	@echo "  make db-bash         - Open bash shell in PostgreSQL container"
	@echo "  make db-init-scripts - Run all SQL scripts in ./init-scripts/power-tariffs folder"
	@echo "  make db-backup       - Create a database backup (saves to ./backups/)"
	@echo "  make db-restore      - Restore database from backup (FILE=path/to/backup.sql.gz)"
	@echo "  make db-list-backups - List available database backups"
	@echo "  make db-status       - Check database connection status"
	@echo "  make db-info         - Show database connection information"
	@echo ""
	@echo "Database Monitoring:"
	@echo "  make db-size         - Show database size"
	@echo "  make db-tables       - List all tables in the database"
	@echo "  make db-connections  - Show active database connections"
	@echo ""
	@echo "Development:"
	@echo "  make setup           - Initial setup - create directories and start services"
	@echo "  make dev             - Start services and show logs"
	@echo "  make fresh           - Stop everything, clean volumes, and start fresh (WARNING!)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           - Stop containers and remove volumes (WARNING: Deletes all data!)"
	@echo "  make prune           - Remove all unused containers, networks, images"
	@echo ""
	@echo "Deployment:"
	@echo "  make push-staging-image  - Push backend Docker image to eg-staging-registry staging ECR"
	@echo "  make push-sandbox-image  - Push backend Docker image to eg-sandbox-registry sandbox ECR"
	@echo "  make push-production-image  - Push backend Docker image to eg-production-registry production ECR"
	@echo '  promote-staging-to-sandbox-image Promote backend Docker image from sandbox to prod (provide TAG: make promote-staging-to-sandbox-image TAG=exampletag)'


# Docker Compose Commands
.PHONY: up
up: ## Start all services in the background
	docker-compose -f $(COMPOSE_FILE) up -d

.PHONY: down
down: ## Stop and remove all containers
	docker-compose -f $(COMPOSE_FILE) down

.PHONY: start
start: ## Start existing containers
	docker-compose -f $(COMPOSE_FILE) start

.PHONY: stop
stop: ## Stop running containers without removing them
	docker-compose -f $(COMPOSE_FILE) stop

.PHONY: restart
restart: ## Restart all services
	docker-compose -f $(COMPOSE_FILE) restart

.PHONY: logs
logs: ## Show logs for all services
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: logs-db
logs-db: ## Show logs for PostgreSQL only
	docker-compose -f $(COMPOSE_FILE) logs -f postgres

.PHONY: ps
ps: ## Show status of all containers
	docker-compose -f $(COMPOSE_FILE) ps

# Database Management
.PHONY: db-shell
db-shell: ## Connect to PostgreSQL shell
	docker exec -it $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)

.PHONY: db-bash
db-bash: ## Open bash shell in PostgreSQL container
	docker exec -it $(DB_CONTAINER) /bin/sh

.PHONY: db-init-scripts
db-init-scripts: ## Run all SQL scripts in ./init-scripts/power-tariffs folder
	@echo "Running initialization scripts from ./init-scripts/power-tariffs..."
	@if [ -d "./init-scripts/power-tariffs" ]; then \
		for script in ./init-scripts/power-tariffs/*.sql; do \
			if [ -f "$$script" ]; then \
				echo "Running $$script..."; \
				docker exec -i $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME) < "$$script" || { echo "Error running $$script"; exit 1; }; \
				echo "✓ Completed $$script"; \
			fi; \
		done; \
		echo "All initialization scripts completed successfully"; \
	else \
		echo "No ./init-scripts/power-tariffs directory found"; \
		exit 1; \
	fi

.PHONY: db-backup
db-backup: ## Create a database backup (saves to ./backups/)
	@mkdir -p ./backups
	@echo "Creating backup..."
	docker exec $(DB_CONTAINER) pg_dump -U $(DB_USER) $(DB_NAME) | gzip > ./backups/backup_$(shell date +%Y%m%d_%H%M%S).sql.gz
	@echo "Backup saved to ./backups/backup_$(shell date +%Y%m%d_%H%M%S).sql.gz"

.PHONY: db-restore
db-restore: ## Restore database from backup (usage: make db-restore FILE=./backups/backup_YYYYMMDD_HHMMSS.sql.gz)
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify backup file. Usage: make db-restore FILE=./backups/backup_YYYYMMDD_HHMMSS.sql.gz"; \
		exit 1; \
	fi
	@echo "Restoring from $(FILE)..."
	gunzip -c $(FILE) | docker exec -i $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)
	@echo "Restore completed"

.PHONY: db-list-backups
db-list-backups: ## List available database backups
	@echo "Available backups:"
	@ls -la ./backups/*.sql.gz 2>/dev/null || echo "No backups found in ./backups/"

# Cleanup Commands
.PHONY: clean
clean: ## Stop containers and remove volumes (WARNING: Deletes all data!)
	docker-compose -f $(COMPOSE_FILE) down -v

.PHONY: prune
prune: ## Remove all unused containers, networks, images
	docker system prune -af

# Development Helpers
.PHONY: db-status
db-status: ## Check database connection status
	@echo "Checking database status..."
	@docker exec $(DB_CONTAINER) pg_isready -U $(DB_USER) -d $(DB_NAME) || echo "Database is not ready"

.PHONY: db-info
db-info: ## Show database connection information
	@echo "Database Connection Info:"
	@echo "========================="
	@echo "Host: localhost"
	@echo "Port: $(DB_PORT)"
	@echo "Database: $(DB_NAME)"
	@echo "User: $(DB_USER)"
	@echo "Password: $(DB_PASSWORD)"
	@echo ""
	@echo "Connection string: postgresql://$(DB_USER):$(DB_PASSWORD)@localhost:$(DB_PORT)/$(DB_NAME)"

# Monitoring
.PHONY: db-size
db-size: ## Show database size
	@echo "Database sizes:"
	@docker exec $(DB_CONTAINER) psql -U $(DB_USER) -d postgres -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database ORDER BY pg_database_size(pg_database.datname) DESC;"

.PHONY: db-tables
db-tables: ## List all tables in the database
	@docker exec $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME) -c "\dt"

.PHONY: db-connections
db-connections: ## Show active database connections
	@docker exec $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME) -c "SELECT pid, usename, application_name, client_addr, state FROM pg_stat_activity WHERE datname = '$(DB_NAME)';"

# Quick setup
.PHONY: setup
setup: ## Initial setup - create directories and start services
	@echo "Setting up Power Tariffs database..."
	@mkdir -p ./init-scripts ./init-scripts/power-tariffs ./backups
	@make up
	@sleep 3
	@make db-status
	@echo "Setup complete!"

# Development workflow
.PHONY: dev
dev: ## Start services and show logs
	@make up
	@make logs

.PHONY: fresh
fresh: ## Stop everything, clean volumes, and start fresh (WARNING: Deletes all data!)
	@echo "WARNING: This will delete all data!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	@make clean
	@make setup

.PHONY: push-staging-image
push-staging-image:
	@bin/push-image 150867077257.dkr.ecr.eu-west-1.amazonaws.com/eg-staging-registry/power-tariffs

.PHONY: push-production-image
push-production-image:
	@bin/push-image 739275443444.dkr.ecr.eu-west-1.amazonaws.com/eg-production-registry/power-tariffs

.PHONY: promote-staging-to-sandbox-image
promote-staging-to-sandbox-image: ## Promote backend Docker image from staging to sandbox (provide TAG: make promote-staging-to-sandbox-image TAG=exampletag)
	@bin/promote-image 150867077257.dkr.ecr.eu-west-1.amazonaws.com/eg-staging-registry/power-tariffs 150867077257.dkr.ecr.eu-west-1.amazonaws.com/eg-sandbox-registry/power-tariffs $(TAG)


.PHONY: install-hooks
install-hooks:
	@echo "Installing pre-commit hook..."
	@mkdir -p .git/hooks
	@echo '#!/bin/sh' > .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Run ruff format before commit' >> .git/hooks/pre-commit
	@echo 'echo "Running ruff format..."' >> .git/hooks/pre-commit
	@echo 'uv run ruff format' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Stage any files that were formatted' >> .git/hooks/pre-commit
	@echo 'git add -u' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo 'echo "✓ Formatting complete and changes staged."' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✓ Pre-commit hook installed successfully!"

.PHONY: uninstall-hooks
uninstall-hooks:
	@echo "Removing pre-commit hook..."
	@rm -f .git/hooks/pre-commit
	@echo "✓ Pre-commit hook removed!"

.PHONY: check-hooks
check-hooks:
	@if [ -f .git/hooks/pre-commit ]; then \
		echo "✓ Pre-commit hook is installed"; \
		echo "Content:"; \
		cat .git/hooks/pre-commit; \
	else \
		echo "✗ Pre-commit hook is not installed"; \
		echo "Run 'make install-hooks' to install"; \
	fi
