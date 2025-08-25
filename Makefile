# Makefile for local development tasks
#
# This Makefile provides a set of generic, well-documented targets to help
# developers interact with the project in a consistent way. It uses the Gradle
# Wrapper (./gradlew) so no global Gradle installation is required.
#

SHELL := /bin/bash

# Default target
.DEFAULT_GOAL := help

# Colors for pretty help output
YELLOW := \033[33m
GREEN  := \033[32m
CYAN   := \033[36m
RESET  := \033[0m

# Internal helper for ensuring gradlew is executable
.PHONY: _ensure-gradlew
_ensure-gradlew:
	@if [[ ! -x ./gradlew ]]; then \
	  echo -e "$(YELLOW)[make] Gradle Wrapper is not executable. Fixing...$(RESET)"; \
	  chmod +x ./gradlew; \
	fi

# Show beautiful help menu with banners, grouping, and formatting
.PHONY: help
help:
	@echo -e "$(CYAN)"
	@echo -e "╔══════════════════════════════════════════════════════════════════════╗"
	@echo -e "║       🚀  Welcome to the Project Dev Make Menu  🚀                  ║"
	@echo -e "╠══════════════════════════════════════════════════════════════════════╣"
	@echo -e "║  To run a target above, use: $(YELLOW)make <target>$(CYAN)                       ║"
	@echo -e "╚══════════════════════════════════════════════════════════════════════╝"
	@echo -e "$(RESET)"
	@echo -e "$(CYAN)Main Development Targets:$(RESET)"
	@awk 'BEGIN {FS=":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ && ($$1=="run"||$$1=="check"||$$1=="clean"||$$1=="lint") { printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sort
	@echo ""
	@echo -e "$(CYAN)Git/CI Workflow Targets:$(RESET)"
	@awk 'BEGIN {FS=":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ && ($$1 ~ /hooks/) { printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sort
	@echo ""
	@echo -e "$(CYAN)All Available Targets:$(RESET)"
	@awk 'BEGIN {FS=":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ { printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sort
	@echo ""
	@echo -e "For detailed usage, see comments or sources in the Makefile itself."

# Run code formatter and linter
.PHONY: lint
lint: _ensure-gradlew ## Format code and run linter
	./gradlew --no-daemon ktfmtFormat detekt

# Run Gradle check (compilation + tests + static checks)
.PHONY: check
check: _ensure-gradlew ## Run Gradle checks (tests, static analysis)
	./gradlew --no-daemon check

# Run the application locally via Spring Boot
.PHONY: run
run: _ensure-gradlew ## Run the Spring Boot application locally
	./gradlew --no-daemon bootRun --args='--spring.profiles.active=dev'

# Clean build artifacts
.PHONY: clean
clean: _ensure-gradlew ## Clean build artifacts
	./gradlew --no-daemon clean

# Install Git hooks by setting core.hooksPath and ensuring executable bits
.PHONY: hooks-install
hooks-install: ## Install Git hooks (pre-commit runs Gradle check)
	@if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
	  echo "[make] Not inside a Git repository."; \
	  exit 1; \
	fi
	git config core.hooksPath .githooks
	chmod +x .githooks/* 2>/dev/null || true
	@echo "[make] Git hooks installed (core.hooksPath -> .githooks)."
	@echo "[make] Pre-commit will run: ./gradlew check"

# Uninstall Git hooks by unsetting the custom hooks path
.PHONY: hooks-uninstall
hooks-uninstall: ## Uninstall custom Git hooks path for this repository
	@if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
	  echo "[make] Not inside a Git repository."; \
	  exit 1; \
	fi
	git config --unset core.hooksPath || true
	@echo "[make] Custom hooks path removed. Git will use .git/hooks again."

# Start service dependencies (e.g., databases) via Docker Compose
.PHONY: start-deps
start-deps: ## Start service dependencies (docker compose up -d)
	docker compose up -d

# Stop service dependencies (e.g., databases) via Docker Compose
.PHONY: stop-deps
stop-deps: ## Stop service dependencies (docker compose down)
	docker compose down
