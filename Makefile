.PHONY: install extract transform visualise orchestration test clean lint format help

help:
	@echo "Available commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make extract       - Run data extraction"
	@echo "  make transform     - Run dbt transformations"
	@echo "  make visualise     - Plot candlestick chart"
	@echo "  make pipeline      - Run full ELT pipeline"
	@echo "  make orchestration - Launch dagster orchestrator and open UI client"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Check code quality"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean generated files"

install:
	uv sync
	uv run dbt compile --project-dir dbt_project/crypto_pipeline --profiles-dir dbt_project

extract:
	uv run python extraction/extract_crypto.py

transform:
	uv run dbt run --project-dir dbt_project/crypto_pipeline --profiles-dir dbt_project

visualise:
	uv run python visualisation/plot_candlesticks.py

pipeline: extract transform
	@echo "✓ Pipeline completed successfully"

orchestration:
	dagster dev -f orchestration/__init__.py

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	rm -rf data/*.duckdb
	rm -rf dbt_project/target/
	rm -rf dbt_project/logs/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
