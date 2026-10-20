.PHONY: up ingest transform export docs site pipeline down

# As etapas dependem uma da outra pela ordem: com make -j o transform rodaria
# antes de a ingestão terminar.
.NOTPARALLEL:

up:
	docker compose up -d --wait

ingest:
	uv run python ingest/ingest_bcb.py

transform:
	cd dbt_bcb && uv run dbt deps --profiles-dir . && uv run dbt build --profiles-dir .

export:
	uv run python export/export_site.py

# Documentação do dbt como página estática, publicada junto com o site em /dbt/.
docs:
	cd dbt_bcb && uv run dbt docs generate --static --profiles-dir .
	mkdir -p site/dbt && cp dbt_bcb/target/static_index.html site/dbt/index.html

site: export
	@echo "abra http://localhost:8002"
	uv run python -m http.server 8002 -d site

pipeline: up ingest transform export

down:
	docker compose down
