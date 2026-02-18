from dagster import AssetExecutionContext, asset

from orchestration.configs.pipe_config import VisualisationConfig
from orchestration.resources.duckdb import DuckdbResource
from visualisation.plot_candlesticks import plot_candlesticks


@asset(
    group_name="visualisation",
    description="Candlestick chart generated from daily OHLC data",
    deps=["daily_candlesticks"],
)
def candlestick_chart(
    context: AssetExecutionContext,
    config: VisualisationConfig,
    duckdb: DuckdbResource,
) -> None:
    conn = duckdb.get_connection()
    plot_candlesticks(conn=conn, coin_id=config.coin_id, vs_currency=config.vs_currency)
    context.log.info(
        f"Candlestick chart generated for {config.coin_id} ({config.vs_currency.upper()})"
    )
