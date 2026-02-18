from pathlib import Path

from dagster import Definitions
from dagster_dbt import DbtCliResource

from orchestration.assets.dbt_assets import crypto_dbt_assets
from orchestration.assets.extraction import raw_crypto_prices
from orchestration.assets.visualisation import candlestick_chart
from orchestration.jobs.crypto_pipeline import crypto_pipeline_job
from orchestration.resources.coingecko import CoinGeckResource
from orchestration.resources.duckdb import DuckdbResource
from orchestration.schedules.daily_schedule import daily_crypto_pipeline_schedule

PROJECT_ROOT = Path(__file__).parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project" / "crypto_pipeline"
DB_PATH = str(PROJECT_ROOT / "data" / "crypto.duckdb")

defs = Definitions(
    assets=[raw_crypto_prices, crypto_dbt_assets, candlestick_chart],
    jobs=[crypto_pipeline_job],
    schedules=[daily_crypto_pipeline_schedule],
    resources={
        "coingecko": CoinGeckResource(db_path=DB_PATH),
        "duckdb": DuckdbResource(db_path=DB_PATH),
        "dbt": DbtCliResource(
            project_dir=str(DBT_PROJECT_DIR),
            profiles_dir=str(DBT_PROJECT_DIR.parent),
            dbt_executable="dbt",
            global_config_flags=[],
            env={"DBT_DB_PATH": DB_PATH},
        ),
    },
)
