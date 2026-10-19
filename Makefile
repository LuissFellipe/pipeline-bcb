.PHONY: up ingest transform pipeline down

up:
	docker compose up -d --wait

ingest:
	uv run python ingest/ingest_bcb.py

transform:
	cd dbt_bcb && uv run dbt build --profiles-dir .

pipeline: up ingest transform

down:
	docker compose down
