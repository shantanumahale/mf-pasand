.PHONY: dev test ingest lint

# Start the API server in development mode with hot-reload
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run the test suite
test:
	pytest -v

# Run the full data ingestion pipeline
ingest:
	python3 -m app.ingestion.ingest

# Start all services via Docker Compose
up:
	docker compose up -d

# Stop all services
down:
	docker compose down

# Rebuild and restart
rebuild:
	docker compose up -d --build
