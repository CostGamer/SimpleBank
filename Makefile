.PHONY: help up down down-clean test logs

help:
	@echo "Available commands:"
	@echo "  make up          - Start Docker containers"
	@echo "  make down        - Stop Docker containers"
	@echo "  make down-clean  - Stop containers and remove volumes"
	@echo "  make test        - Run tests in Docker container"
	@echo "  make logs        - Show Docker logs"

up:
	docker-compose up -d

down:
	docker-compose down

down-clean:
	docker-compose down -v --rmi local --remove-orphans

test:
	docker-compose exec app pytest -v

logs:
	docker-compose logs -f app
