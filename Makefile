.PHONY: up down test test-backend test-frontend test-oncall incident

up:
	docker compose up --build

down:
	docker compose down

test: test-backend test-frontend test-oncall

test-backend:
	PYTHONPATH=backend python -m pytest backend/tests

test-frontend:
	npm --prefix frontend ci
	npm --prefix frontend test -- --run
	npm --prefix frontend run build

test-oncall:
	PYTHONPATH=oncall python -m pytest oncall/tests

incident:
	powershell -ExecutionPolicy Bypass -File scripts/demo-incident.ps1

