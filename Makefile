.PHONY: help up down build logs shell dbshell migrate makemigrations test test-create-db lint format seed createsuperuser token

help:
	@echo "Available commands:"
	@echo "  make up              Start the application with Docker Compose"
	@echo "  make down            Stop containers"
	@echo "  make build           Build containers"
	@echo "  make logs            Show container logs"
	@echo "  make shell           Open a shell in the web container"
	@echo "  make dbshell         Open a psql shell in the db container"
	@echo "  make migrate         Run database migrations"
	@echo "  make makemigrations  Create new migrations"
	@echo "  make test            Run tests"
	@echo "  make test-create-db  Recreate test database and run tests"
	@echo "  make lint            Run Ruff lint checks"
	@echo "  make format          Format code with Ruff"
	@echo "  make seed            Seed demo data"
	@echo "  make createsuperuser Create a Django superuser"
	@echo "  make token USER=...  Create a DRF auth token for a user"

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

shell:
	docker compose exec web sh

dbshell:
	docker compose exec db psql -U admin -d patient_monitoring

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

test:
	docker compose exec web pytest

test-create-db:
	docker compose exec web pytest --create-db

lint:
	docker compose exec web ruff check .

format:
	docker compose exec web ruff check . --fix
	docker compose exec web ruff format .

seed:
	docker compose exec db psql -U admin -d patient_monitoring -f /seed.sql

createsuperuser:
	docker compose exec web python manage.py createsuperuser

token:
	docker compose exec web python manage.py drf_create_token $(USER)
