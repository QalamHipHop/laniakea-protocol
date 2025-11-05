# Laniakea Protocol Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help install dev test lint format clean build deploy docker

# Default target
help:
	@echo "Laniakea Protocol - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies"
	@echo "  dev         Start development server"
	@echo "  test        Run tests"
	@echo "  lint        Run code quality checks"
	@echo "  format      Format code with black and isort"
	@echo "  clean       Clean temporary files"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-run      Run Docker container"
	@echo "  docker-stop     Stop Docker containers"
	@echo "  docker-clean    Clean Docker resources"
	@echo ""
	@echo "Deployment:"
	@echo "  build       Build for production"
	@echo "  deploy      Deploy to production"
	@echo ""
	@echo "Database:"
	@echo "  db-init     Initialize database"
	@echo "  db-migrate  Run database migrations"
	@echo "  db-reset    Reset database"

# Installation
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# Development
dev:
	@echo "Starting development server..."
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dev-docker:
	@echo "Starting development with Docker..."
	docker-compose -f docker-compose.yml up --build

# Testing
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-fast:
	@echo "Running fast tests..."
	pytest tests/ -x --tb=short

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v

test-performance:
	@echo "Running performance tests..."
	pytest tests/performance/ -v

# Code Quality
lint:
	@echo "Running linting checks..."
	flake8 src/ tests/
	mypy src/
	bandit -r src/
	safety check

format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/

format-check:
	@echo "Checking code formatting..."
	black --check src/ tests/
	isort --check-only src/ tests/

# Security
security-scan:
	@echo "Running security scan..."
	bandit -r src/ -f json -o bandit-report.json
	safety check --json --output safety-report.json
	semgrep --config=auto src/

# Database
db-init:
	@echo "Initializing database..."
	python -m src.database.init_db

db-migrate:
	@echo "Running database migrations..."
	python -m src.database.migrate

db-reset:
	@echo "Resetting database..."
	python -m src.database.reset

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t laniakea-protocol .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 --name laniakea laniakea-protocol

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down || true
	docker stop laniakea || true

docker-clean:
	@echo "Cleaning Docker resources..."
	docker-compose down -v || true
	docker system prune -f

# Production
build:
	@echo "Building for production..."
	docker build --target production -t laniakea-protocol:latest .

deploy-staging:
	@echo "Deploying to staging..."
	docker-compose -f docker-compose.staging.yml up -d

deploy-production:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.yml up -d

# Utilities
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

logs:
	@echo "Showing logs..."
	docker-compose logs -f

backup:
	@echo "Creating backup..."
	./scripts/backup.sh

health:
	@echo "Checking health..."
	curl -f http://localhost:8000/health || echo "Service not healthy"

# Monitoring
metrics:
	@echo "Opening metrics dashboard..."
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000"

# Documentation
docs:
	@echo "Building documentation..."
	mkdocs build

docs-serve:
	@echo "Serving documentation..."
	mkdocs serve

# Release
version:
	@echo "Current version: $(shell python -c 'import main; print(main.VERSION)')"

bump-patch:
	@echo "Bumping patch version..."
	bump2version patch

bump-minor:
	@echo "Bumping minor version..."
	bump2version minor

bump-major:
	@echo "Bumping major version..."
	bump2version major

# Development helpers
install-hooks:
	@echo "Installing git hooks..."
	pre-commit install

check-all:
	@echo "Running all checks..."
	make format-check
	make lint
	make test
	make security-scan

ci:
	@echo "Running CI pipeline..."
	make format-check
	make lint
	make test
	make security-scan
	make docker-build

# Quick development commands
quick-test:
	@echo "Quick test run..."
	pytest tests/ --tb=short -q

quick-lint:
	@echo "Quick lint check..."
	flake8 src/ --max-line-length=100

quick-format:
	@echo "Quick format..."
	black src/ -q
	isort src/ -q

# Environment setup
env-dev:
	@echo "Setting up development environment..."
	cp .env.example .env.dev
	@echo "Please edit .env.dev with your configuration"

env-prod:
	@echo "Setting up production environment..."
	cp .env.example .env.prod
	@echo "Please edit .env.prod with your production configuration"

# Database shortcuts
db-shell:
	@echo "Opening database shell..."
	docker-compose exec postgres psql -U laniakea -d laniakea

redis-shell:
	@echo "Opening Redis shell..."
	docker-compose exec redis redis-cli

# Utility commands
tree-dirs:
	@echo "Showing directory structure..."
	tree -I '__pycache__|*.pyc|.git|node_modules'

find-large-files:
	@echo "Finding large files..."
	find . -type f -size +10M -exec ls -lh {} \;

count-lines:
	@echo "Counting lines of code..."
	find src/ -name "*.py" | xargs wc -l

# Git utilities
git-clean:
	@echo "Cleaning git..."
	git clean -fd
	git gc --aggressive --prune=now

git-stats:
	@echo "Git statistics..."
	git shortlog -sn