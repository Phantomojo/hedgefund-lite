# 🏦 HEDGE FUND LITE - Production Makefile
# Comprehensive trading system management

.PHONY: help dev build test deploy monitor clean logs backup restore emergency-stop

# Configuration
PYTHON = python3
PIP = pip3
VENV = venv
APP_NAME = hedgefund-lite
DOCKER_IMAGE = hedgefund-lite:latest
DOCKER_CONTAINER = hedgefund-lite-container

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)🏦 HEDGE FUND LITE - Production Trading System$(NC)"
	@echo "$(YELLOW)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ============================================================================
# Development Commands
# ============================================================================

dev: ## Start development environment
	@echo "$(BLUE)🚀 Starting development environment...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)Creating virtual environment...$(NC)"; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@echo "$(GREEN)Activating virtual environment...$(NC)"
	@source $(VENV)/bin/activate && \
	$(PIP) install -r requirements.txt && \
	echo "$(GREEN)✅ Development environment ready!$(NC)"

install: ## Install dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@source $(VENV)/bin/activate && \
	$(PIP) install -r requirements.txt && \
	echo "$(GREEN)✅ Dependencies installed!$(NC)"

test: ## Run all tests
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@source $(VENV)/bin/activate && \
	pytest tests/ -v --cov=src --cov-report=html && \
	echo "$(GREEN)✅ Tests completed!$(NC)"

lint: ## Run code linting
	@echo "$(BLUE)🔍 Running code linting...$(NC)"
	@source $(VENV)/bin/activate && \
	black src/ tests/ && \
	isort src/ tests/ && \
	flake8 src/ tests/ && \
	echo "$(GREEN)✅ Code linting completed!$(NC)"

# ============================================================================
# Production Commands
# ============================================================================

build: ## Build production Docker image
	@echo "$(BLUE)🏗️ Building production image...$(NC)"
	@docker build -t $(DOCKER_IMAGE) . && \
	echo "$(GREEN)✅ Production image built!$(NC)"

deploy: ## Deploy to production
	@echo "$(BLUE)🚀 Deploying to production...$(NC)"
	@docker-compose up -d && \
	echo "$(GREEN)✅ Production deployment complete!$(NC)"

up: ## Start all services
	@echo "$(BLUE)🔄 Starting all services...$(NC)"
	@docker-compose up -d && \
	echo "$(GREEN)✅ All services started!$(NC)"

down: ## Stop all services
	@echo "$(BLUE)🛑 Stopping all services...$(NC)"
	@docker-compose down && \
	echo "$(GREEN)✅ All services stopped!$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)🔄 Restarting all services...$(NC)"
	@docker-compose restart && \
	echo "$(GREEN)✅ All services restarted!$(NC)"

# ============================================================================
# Monitoring Commands
# ============================================================================

monitor: ## Start monitoring dashboard
	@echo "$(BLUE)📊 Starting monitoring dashboard...$(NC)"
	@source $(VENV)/bin/activate && \
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload && \
	echo "$(GREEN)✅ Monitoring dashboard started!$(NC)"

status: ## Check system status
	@echo "$(BLUE)📈 Checking system status...$(NC)"
	@curl -s http://localhost:8000/health | jq . || \
	echo "$(RED)❌ System not responding$(NC)"

logs: ## View system logs
	@echo "$(BLUE)📋 Viewing system logs...$(NC)"
	@docker-compose logs -f --tail=100

logs-app: ## View application logs
	@echo "$(BLUE)📋 Viewing application logs...$(NC)"
	@docker-compose logs -f app --tail=100

logs-db: ## View database logs
	@echo "$(BLUE)📋 Viewing database logs...$(NC)"
	@docker-compose logs -f db --tail=100

logs-redis: ## View Redis logs
	@echo "$(BLUE)📋 Viewing Redis logs...$(NC)"
	@docker-compose logs -f redis --tail=100

# ============================================================================
# Database Commands
# ============================================================================

db-migrate: ## Run database migrations
	@echo "$(BLUE)🗄️ Running database migrations...$(NC)"
	@source $(VENV)/bin/activate && \
	alembic upgrade head && \
	echo "$(GREEN)✅ Database migrations completed!$(NC)"

db-reset: ## Reset database (WARNING: Destructive)
	@echo "$(RED)⚠️ WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && \
	if [ "$$confirm" = "y" ]; then \
		docker-compose down -v && \
		docker-compose up -d db && \
		sleep 5 && \
		$(MAKE) db-migrate && \
		echo "$(GREEN)✅ Database reset complete!$(NC)"; \
	else \
		echo "$(YELLOW)Database reset cancelled$(NC)"; \
	fi

db-backup: ## Backup database
	@echo "$(BLUE)💾 Creating database backup...$(NC)"
	@docker-compose exec db pg_dump -U trading hedgefund > backup_$(shell date +%Y%m%d_%H%M%S).sql && \
	echo "$(GREEN)✅ Database backup created!$(NC)"

db-restore: ## Restore database from backup
	@echo "$(BLUE)📥 Restoring database from backup...$(NC)"
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)❌ Please specify BACKUP_FILE=filename.sql$(NC)"; \
		exit 1; \
	fi
	@docker-compose exec -T db psql -U trading hedgefund < $(BACKUP_FILE) && \
	echo "$(GREEN)✅ Database restored!$(NC)"

# ============================================================================
# Trading System Commands
# ============================================================================

start-trading: ## Start automated trading
	@echo "$(BLUE)🤖 Starting automated trading...$(NC)"
	@source $(VENV)/bin/activate && \
	python scripts/start_trading.py && \
	echo "$(GREEN)✅ Automated trading started!$(NC)"

stop-trading: ## Stop automated trading
	@echo "$(BLUE)🛑 Stopping automated trading...$(NC)"
	@curl -X POST http://localhost:8000/api/v1/trading/emergency-stop && \
	echo "$(GREEN)✅ Automated trading stopped!$(NC)"

emergency-stop: ## Emergency stop all trading (CRITICAL)
	@echo "$(RED)🚨 EMERGENCY STOP - STOPPING ALL TRADING!$(NC)"
	@curl -X POST http://localhost:8000/api/v1/trading/emergency-stop && \
	docker-compose restart app && \
	echo "$(GREEN)✅ Emergency stop executed!$(NC)"

trading-status: ## Check trading system status
	@echo "$(BLUE)📊 Checking trading system status...$(NC)"
	@curl -s http://localhost:8000/api/v1/trading/status | jq . || \
	echo "$(RED)❌ Trading system not responding$(NC)"

risk-status: ## Check risk management status
	@echo "$(BLUE)🛡️ Checking risk management status...$(NC)"
	@curl -s http://localhost:8000/api/v1/risk/status | jq . || \
	echo "$(RED)❌ Risk system not responding$(NC)"

# ============================================================================
# Data Management Commands
# ============================================================================

data-sync: ## Sync data from all sources
	@echo "$(BLUE)🔄 Syncing data from all sources...$(NC)"
	@source $(VENV)/bin/activate && \
	python scripts/sync_data.py && \
	echo "$(GREEN)✅ Data sync completed!$(NC)"

data-backup: ## Backup all data
	@echo "$(BLUE)💾 Creating data backup...$(NC)"
	@tar -czf data_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz data/ && \
	echo "$(GREEN)✅ Data backup created!$(NC)"

data-restore: ## Restore data from backup
	@echo "$(BLUE)📥 Restoring data from backup...$(NC)"
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)❌ Please specify BACKUP_FILE=filename.tar.gz$(NC)"; \
		exit 1; \
	fi
	@tar -xzf $(BACKUP_FILE) && \
	echo "$(GREEN)✅ Data restored!$(NC)"

# ============================================================================
# Maintenance Commands
# ============================================================================

clean: ## Clean up temporary files
	@echo "$(BLUE)🧹 Cleaning up temporary files...$(NC)"
	@find . -type f -name "*.pyc" -delete && \
	find . -type d -name "__pycache__" -delete && \
	find . -type d -name "*.egg-info" -exec rm -rf {} + && \
	echo "$(GREEN)✅ Cleanup completed!$(NC)"

clean-all: ## Clean everything (WARNING: Destructive)
	@echo "$(RED)⚠️ WARNING: This will delete all data and containers!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && \
	if [ "$$confirm" = "y" ]; then \
		docker-compose down -v --remove-orphans && \
		docker system prune -f && \
		rm -rf data/ logs/ && \
		echo "$(GREEN)✅ Complete cleanup finished!$(NC)"; \
	else \
		echo "$(YELLOW)Cleanup cancelled$(NC)"; \
	fi

update: ## Update system and dependencies
	@echo "$(BLUE)🔄 Updating system...$(NC)"
	@git pull origin main && \
	$(MAKE) install && \
	$(MAKE) build && \
	$(MAKE) deploy && \
	echo "$(GREEN)✅ System updated!$(NC)"

# ============================================================================
# Development Tools
# ============================================================================

shell: ## Open Python shell
	@echo "$(BLUE)🐍 Opening Python shell...$(NC)"
	@source $(VENV)/bin/activate && \
	python

jupyter: ## Start Jupyter notebook
	@echo "$(BLUE)📓 Starting Jupyter notebook...$(NC)"
	@source $(VENV)/bin/activate && \
	jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser

# ============================================================================
# Security Commands
# ============================================================================

security-scan: ## Run security scan
	@echo "$(BLUE)🔒 Running security scan...$(NC)"
	@source $(VENV)/bin/activate && \
	bandit -r src/ && \
	safety check && \
	echo "$(GREEN)✅ Security scan completed!$(NC)"

rotate-keys: ## Rotate API keys
	@echo "$(BLUE)🔑 Rotating API keys...$(NC)"
	@python scripts/rotate_keys.py && \
	echo "$(GREEN)✅ API keys rotated!$(NC)"

# ============================================================================
# Performance Commands
# ============================================================================

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)⚡ Running performance benchmarks...$(NC)"
	@source $(VENV)/bin/activate && \
	python scripts/benchmark.py && \
	echo "$(GREEN)✅ Benchmarks completed!$(NC)"

stress-test: ## Run stress tests
	@echo "$(BLUE)🔥 Running stress tests...$(NC)"
	@source $(VENV)/bin/activate && \
	python scripts/stress_test.py && \
	echo "$(GREEN)✅ Stress tests completed!$(NC)"

# ============================================================================
# Utility Commands
# ============================================================================

version: ## Show system version
	@echo "$(BLUE)📋 System version information:$(NC)"
	@echo "App: $(APP_NAME)"
	@echo "Docker Image: $(DOCKER_IMAGE)"
	@echo "Python: $$(python3 --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"

config: ## Show configuration
	@echo "$(BLUE)⚙️ Current configuration:$(NC)"
	@docker-compose config

ps: ## Show running processes
	@echo "$(BLUE)📋 Running processes:$(NC)"
	@docker-compose ps

top: ## Show resource usage
	@echo "$(BLUE)📊 Resource usage:$(NC)"
	@docker stats --no-stream

# ============================================================================
# Quick Start Commands
# ============================================================================

quickstart: ## Quick start for development
	@echo "$(BLUE)🚀 Quick start for development...$(NC)"
	@$(MAKE) dev
	@$(MAKE) up
	@$(MAKE) db-migrate
	@echo "$(GREEN)✅ Quick start complete! Access at http://localhost:8000$(NC)"

production-start: ## Production deployment
	@echo "$(BLUE)🚀 Production deployment...$(NC)"
	@$(MAKE) build
	@$(MAKE) deploy
	@$(MAKE) db-migrate
	@$(MAKE) start-trading
	@echo "$(GREEN)✅ Production deployment complete!$(NC)"

# ============================================================================
# Troubleshooting Commands
# ============================================================================

debug: ## Debug mode
	@echo "$(BLUE)🐛 Starting debug mode...$(NC)"
	@source $(VENV)/bin/activate && \
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

check-deps: ## Check dependencies
	@echo "$(BLUE)🔍 Checking dependencies...$(NC)"
	@source $(VENV)/bin/activate && \
	pip list --outdated

fix-permissions: ## Fix file permissions
	@echo "$(BLUE)🔧 Fixing file permissions...$(NC)"
	@chmod +x scripts/*.py && \
	chmod 600 .env && \
	echo "$(GREEN)✅ Permissions fixed!$(NC)"

# ============================================================================
# Documentation Commands
# ============================================================================

docs: ## Generate documentation
	@echo "$(BLUE)📚 Generating documentation...$(NC)"
	@source $(VENV)/bin/activate && \
	mkdocs build && \
	echo "$(GREEN)✅ Documentation generated!$(NC)"

docs-serve: ## Serve documentation
	@echo "$(BLUE)📚 Serving documentation...$(NC)"
	@source $(VENV)/bin/activate && \
	mkdocs serve

# ============================================================================
# Default target
# ============================================================================

.DEFAULT_GOAL := help
