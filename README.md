# Lydia Interview - ELT Pipeline

## Overview
ELT pipeline for cryptocurrency data using API connection, DuckDB, dbt and orchestrated with dagster.

## Tech Stack
- **Extraction**: Direct REST API (CoinGecko) 
- **Loading**: DuckDB
- **Transformation**: dbt
- **Orchestration**: Dagster
- **Dependency Management**: uv


## Project Structure
```
lydia-interview/
├── extraction/          # Direct CoinGecko API extraction
├── dbt_project/         # dbt models (staging + marts)
│   └── crypto_pipeline/
│       └── models/
│           ├── staging/ # stg_crypto_prices (view)
│           └── marts/   # daily_candlesticks (incremental)
├── orchestration/       # Dagster assets, jobs, schedules
├── visualisation/       # Candlestick chart generation
├── tests/               # Unit tests
└── data/                # DuckDB database
```


# Design Decisions

## Direct API vs PyAirbyte

The assignment specified using PyAirbyte for data extraction. However, the `source-coingecko-coins` connector is currently broken, returning `unprocessableEntity` errors both locally and on Airbyte's web platform (verified February 2025). After investigating the issue and testing multiple configurations, I implemented direct REST API calls to CoinGecko's public endpoint instead. This maintains the ELT architecture (Extract → Load → Transform).

## DBT 
dbt handles the transformation layer with two models:
- stg_crypto_prices (view) -> cleans and validates raw data, flags invalid prices
- daily_candlesticks (incremental table) -> Aggregates hourly prices into OHLC (Open Higher Lower Close) candles. The incremental strategy ensures only new days are processed on each run, using price_date + coin_id + vs_currency as the unique key. This makes the pipeline efficient and idempotent, running it multiple times produces the same result.

## Dagster for orchestration

I chose Dagster instead of Airflow (For Prefect I can't juge I never use it nor never saw template or code snippet), cause I prefer the asset orientation philosophy, here the software define the assets, not just the tasks. This give us a better data genealogy and more clear flow of events. Also even the UI looks better, more modern (but it's a personal preference here). This make the design of the whole orchestrator very easy to understand, every part is encapsulated, each do his purpose.

## Idempotency
Both the extraction layer and the transform layer are idempotent:
- The Extraction uses INSERT OR REPLACE on (timestamp, coin_id, vs_currency) primary key, with that we avoid the creation of duplicates data
- DBT follow the same principles with a incremental model based on mostly the same primary key (price_date, coin_id, vs_currency)

## Setup
```bash
# Install dependencies
make install

# Run the pipeline with orchestrator, open http://localhost:3000 to access Dagster UI
make orchestration

# Run the pipeline without orchestrator
make pipeline

# Print all the different commands (if you want to isolate parts of the project)
make help
```

## Overriding Pipeline Parameters

Each asset exposes runtime configuration through Dagster's Launchpad.

**How to override:**
1. Go to **Jobs** → `crypto_pipeline` → **Launchpad** tab
2. Paste a config override in the YAML editor
3. Click **Launch Run**

**Extraction config** (which coins to fetch, time range):
```yaml
ops:
  raw_crypto_prices:
    config:
      coin_id:
        - bitcoin
        - solana
      vs_currency: "eur"
      days: 30
      rate_limit_delay: 1.5
```

**Visualisation config** (which coin to plot):
```yaml
ops:
  candlestick_chart:
    config:
      coin_id: "bitcoin"
      vs_currency: "usd"
```

> **Note:** The visualisation asset (`candlestick_chart`) is part of `AssetSelection.all()` but must be triggered manually from the Assets view when running it standalone, as it depends on `daily_candlesticks` being materialized first. When running the full `crypto_pipeline` job it will execute automatically after the dbt assets.

> **Note on config persistence:** The open-source Dagster UI does not save config presets between runs. Default values are defined in `orchestration/configs/pipe_config.py` and serve as the baseline for every run.

## Development
```bash
make format    # Format code
make lint      # Check code quality
make test      # Run tests
```
