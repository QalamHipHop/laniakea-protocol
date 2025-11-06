# 🌌 Laniakea Protocol v0.0.02 - Unified Makefile
# Makefile یکپارچه برای مدیریت و deployment پروژه

.PHONY: help install dev test build deploy clean logs monitor health
.DEFAULT_GOAL := help

# Configuration
PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose
NODE_ID := laniakea-node-001
PORT := 8000
HOST := 0.0.0.0

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

help: ## Show this help message
	@echo "$(PURPLE)🌌 Laniakea Protocol v0.0.02 - Unified Makefile$(RESET)"
	@echo "$(CYAN)Usage: make [target]$(RESET)"
	@echo ""
	@echo "$(GREEN)📦 Setup & Installation$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /setup|install/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)🚀 Development$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /dev|test|lint/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)🐳 Docker$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /docker|build/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)🚀 Deployment$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /deploy|prod/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)🔧 Operations$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /logs|monitor|health|clean/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ==========================================
# SETUP & INSTALLATION
# ==========================================

setup: ## Setup the project for first time
	@echo "$(BLUE)🔧 Setting up Laniakea Protocol...$(RESET)"
	@$(PYTHON) start.py --interactive
	@echo "$(GREEN)✅ Setup completed!$(RESET)"

install: ## Install dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(RESET)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements_unified.txt
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)📦 Installing development dependencies...$(RESET)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements_unified.txt
	@$(PIP) install pytest pytest-asyncio pytest-cov black flake8 mypy pre-commit
	@echo "$(GREEN)✅ Development dependencies installed$(RESET)"

install-minimal: ## Install minimal dependencies
	@echo "$(BLUE)📦 Installing minimal dependencies...$(RESET)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements_minimal.txt
	@echo "$(GREEN)✅ Minimal dependencies installed$(RESET)"

init: ## Initialize project structure
	@echo "$(BLUE)🏗️ Creating project structure...$(RESET)"
	@mkdir -p data logs backups models cache profiles uploads temp
	@mkdir -p docs/api docs/architecture docs/deployment docs/guides
	@mkdir -p scripts tests monitoring nginx
	@echo "$(GREEN)✅ Project structure created$(RESET)"

# ==========================================
# DEVELOPMENT
# ==========================================

dev: ## Run in development mode
	@echo "$(BLUE)🚀 Starting development server...$(RESET)"
	@$(PYTHON) main_unified.py --node-id $(NODE_ID) --port $(PORT) --dev

dev-enhanced: ## Run in development mode with enhanced features
	@echo "$(BLUE)🚀 Starting enhanced development server...$(RESET)"
	@$(PYTHON) main_unified.py --node-id $(NODE_ID) --port $(PORT) --dev

dev-minimal: ## Run in minimal mode
	@echo "$(BLUE)🚀 Starting minimal server...$(RESET)"
	@$(PYTHON) main_unified.py --node-id $(NODE_ID) --port $(PORT) --disable-enhanced

test: ## Run tests
	@echo "$(BLUE)🧪 Running tests...$(RESET)"
	@$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-fast: ## Run fast tests
	@echo "$(BLUE)🧪 Running fast tests...$(RESET)"
	@$(PYTHON) -m pytest tests/ -v --tb=short

lint: ## Run code linting
	@echo "$(BLUE)🔍 Running linting...$(RESET)"
	@flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503
	@echo "$(GREEN)✅ Linting completed$(RESET)"

format: ## Format code with black
	@echo "$(BLUE)🎨 Formatting code...$(RESET)"
	@black src/ tests/ *.py
	@echo "$(GREEN)✅ Code formatted$(RESET)"

# ==========================================
# DOCKER
# ==========================================

docker-build: ## Build Docker image
	@echo "$(BLUE)🐳 Building Docker image...$(RESET)"
	@$(DOCKER) build -f Dockerfile.unified -t laniakea-protocol:latest .
	@echo "$(GREEN)✅ Docker image built$(RESET)"

docker-run: ## Run Docker container
	@echo "$(BLUE)🐳 Running Docker container...$(RESET)"
	@$(DOCKER) run --rm -p $(PORT):8000 \
		-e NODE_ID=docker-$(NODE_ID) \
		-e PORT=8000 \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		laniakea-protocol:latest

docker-compose-up: ## Start services with docker-compose
	@echo "$(BLUE)🐳 Starting services with docker-compose...$(RESET)"
	@$(DOCKER_COMPOSE) -f docker-compose.unified.yml up -d
	@echo "$(GREEN)✅ Services started$(RESET)"

docker-compose-down: ## Stop services with docker-compose
	@echo "$(BLUE)🐳 Stopping services with docker-compose...$(RESET)"
	@$(DOCKER_COMPOSE) -f docker-compose.unified.yml down
	@echo "$(GREEN)✅ Services stopped$(RESET)"

# ==========================================
# DEPLOYMENT
# ==========================================

deploy-dev: ## Deploy to development environment
	@echo "$(BLUE)🚀 Deploying to development...$(RESET)"
	@$(DOCKER_COMPOSE) -f docker-compose.unified.yml --profile dev up -d
	@echo "$(GREEN)✅ Development deployment completed$(RESET)"

deploy-prod: ## Deploy to production environment
	@echo "$(RED)⚠️ Deploying to production...$(RESET)"
	@read -p "Are you sure you want to deploy to production? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@$(DOCKER_COMPOSE) -f docker-compose.unified.yml up -d
	@echo "$(GREEN)✅ Production deployment completed$(RESET)"

# ==========================================
# OPERATIONS
# ==========================================

logs: ## Show application logs
	@echo "$(BLUE)📋 Showing application logs...$(RESET)"
	@tail -f logs/laniakea.log

health: ## Check application health
	@echo "$(BLUE)🏥 Checking application health...$(RESET)"
	@curl -f http://$(HOST):$(PORT)/health || echo "$(RED)❌ Health check failed$(RESET)"

status: ## Show detailed status
	@echo "$(BLUE)📊 Application Status:$(RESET)"
	@curl -s http://$(HOST):$(PORT)/status | python -m json.tool

clean: ## Clean up temporary files
	@echo "$(BLUE)🧹 Cleaning up...$(RESET)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

info: ## Show project information
	@echo "$(PURPLE)🌌 Laniakea Protocol v0.0.02$(RESET)"
	@echo "$(CYAN)Node ID: $(NODE_ID)$(RESET)"
	@echo "$(CYAN)Port: $(PORT)$(RESET)"
	@echo "$(CYAN)Host: $(HOST)$(RESET)"
	@echo ""
	@echo "$(GREEN)📚 Documentation: http://localhost:$(PORT)/docs$(RESET)"
	@echo "$(GREEN)📊 Dashboard: http://localhost:$(PORT)$(RESET)"
	@echo "$(GREEN)🏥 Health: http://localhost:$(PORT)/health$(RESET)"

version: ## Show version information
	@echo "$(PURPLE)🌌 Laniakea Protocol v0.0.02 Enhanced$(RESET)"
	@echo "$(BLUE)Build: $(shell git rev-parse --short HEAD 2>/dev/null || echo 'unknown')$(RESET)"
	@echo "$(BLUE)Date: $(shell date)$(RESET)"
	@echo "$(BLUE)Python: $(shell $(PYTHON) --version)$(RESET)"