from pathlib import Path

from dagster import AssetExecutionContext
from dagster._core.definitions.policy import RetryPolicy
from dagster_dbt import DbtCliResource, dbt_assets

DBT_PROJECT_DIR = (
    Path(__file__).parent.parent.parent / "dbt_project" / "crypto_pipeline"
)


@dbt_assets(
    retry_policy=RetryPolicy(max_retries=3, delay=5),
    manifest=DBT_PROJECT_DIR / "target" / "manifest.json",
)
def crypto_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["run"], context=context).stream()
