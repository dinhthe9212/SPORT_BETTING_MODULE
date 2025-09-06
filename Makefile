# SPORT_BETTING_MODULE - Makefile
# Commands to manage the microservices project

.PHONY: help build up down logs clean test migrate collectstatic

# Default target
help:
	@echo "SPORT_BETTING_MODULE - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make build          - Build all Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - Show logs from all services"
	@echo "  make clean          - Clean up containers and volumes"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        - Run database migrations using migration service"
	@echo "  make migrate-dev    - Run migrations for development environment"
	@echo "  make migrate-prod   - Run migrations for production environment"
	@echo "  make migrate-force  - Force run migrations (clear locks first)"
	@echo "  make db-reset       - Reset all databases"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run tests for all services"
	@echo "  make test-betting   - Run tests for betting service"
	@echo "  make test-carousel  - Run tests for carousel service"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell          - Open shell in betting service container"
	@echo "  make collectstatic  - Collect static files for all services"
	@echo "  make health         - Check health of all services"
	@echo "  make check-env      - Check environment variables configuration"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Database commands
migrate:
	@echo "Running migration service..."
	docker-compose up migration_service
	@echo "Migration completed successfully!"

migrate-dev:
	@echo "Running migration for development environment..."
	docker-compose -f docker-compose.yml up migration_service
	@echo "Development migration completed!"

migrate-prod:
	@echo "Running migration for production environment..."
	docker-compose -f docker-compose.production.yml up migration_service
	@echo "Production migration completed!"

migrate-force:
	@echo "Force running migration (clearing locks)..."
	docker-compose exec redis redis-cli FLUSHDB
	docker-compose up migration_service
	@echo "Force migration completed!"

db-reset:
	docker-compose down -v
	docker-compose up -d postgres
	sleep 10
	docker-compose up -d

# Testing commands
test:
	docker-compose exec betting_service python manage.py test
	docker-compose exec carousel_service python manage.py test
	docker-compose exec individual_bookmaker_service python manage.py test
	docker-compose exec risk_management_service python manage.py test
	docker-compose exec saga_orchestrator python manage.py test
	docker-compose exec sports_data_service python manage.py test

test-betting:
	docker-compose exec betting_service python manage.py test

test-carousel:
	docker-compose exec carousel_service python manage.py test

test-individual-bookmaker:
	docker-compose exec individual_bookmaker_service python manage.py test

test-risk-management:
	docker-compose exec risk_management_service python manage.py test

test-saga:
	docker-compose exec saga_orchestrator python manage.py test

test-sports-data:
	docker-compose exec sports_data_service python manage.py test

# Utility commands
shell:
	docker-compose exec betting_service bash

shell-carousel:
	docker-compose exec carousel_service bash

shell-individual-bookmaker:
	docker-compose exec individual_bookmaker_service bash

shell-risk-management:
	docker-compose exec risk_management_service bash

shell-saga:
	docker-compose exec saga_orchestrator bash

shell-sports-data:
	docker-compose exec sports_data_service bash

collectstatic:
	docker-compose exec betting_service python manage.py collectstatic --noinput
	docker-compose exec carousel_service python manage.py collectstatic --noinput
	docker-compose exec individual_bookmaker_service python manage.py collectstatic --noinput
	docker-compose exec risk_management_service python manage.py collectstatic --noinput
	docker-compose exec saga_orchestrator python manage.py collectstatic --noinput
	docker-compose exec sports_data_service python manage.py collectstatic --noinput

health:
	@echo "Checking service health..."
	@curl -f http://localhost:8002/health/ && echo " - Betting Service: OK" || echo " - Betting Service: FAIL"
	@curl -f http://localhost:8006/health/ && echo " - Carousel Service: OK" || echo " - Carousel Service: FAIL"
	@curl -f http://localhost:8007/health/ && echo " - Individual Bookmaker Service: OK" || echo " - Individual Bookmaker Service: FAIL"
	@curl -f http://localhost:8003/health/ && echo " - Risk Management Service: OK" || echo " - Risk Management Service: FAIL"
	@curl -f http://localhost:8008/health/ && echo " - Saga Orchestrator: OK" || echo " - Saga Orchestrator: FAIL"
	@curl -f http://localhost:8005/health/ && echo " - Sports Data Service: OK" || echo " - Sports Data Service: FAIL"

check-env:
	@echo "Checking environment variables..."
	@python scripts/check_env.py

# Production commands
prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Backup commands
backup-db:
	docker-compose exec postgres pg_dump -U postgres sport_betting_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db:
	docker-compose exec -T postgres psql -U postgres sport_betting_db < $(FILE)
