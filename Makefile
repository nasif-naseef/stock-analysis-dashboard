.PHONY: help build up down logs restart clean test migrate seed prod-build prod-up

help:
	@echo "Stock Analysis Dashboard - Available Commands"
	@echo "=============================================="
	@echo "make build      - Build all Docker containers"
	@echo "make up         - Start all services"
	@echo "make down       - Stop all services"
	@echo "make logs       - View logs from all services"
	@echo "make restart    - Restart all services"
	@echo "make clean      - Remove all containers, volumes, and images"
	@echo "make test       - Run tests"
	@echo "make migrate    - Run database migrations"
	@echo "make seed       - Seed initial data"
	@echo "make prod-build - Build for production"
	@echo "make prod-up    - Start production environment"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v --rmi all
	@echo "✅ Cleaned up all containers, volumes, and images"

test:
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

migrate:
	docker-compose exec backend alembic upgrade head

seed:
	docker-compose exec backend python -c "from app.database import init_db; init_db()"

prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production services started!"
