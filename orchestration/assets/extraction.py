from dagster import AssetExecutionContext, MetadataValue, Output, RetryPolicy, asset

from orchestration.configs.pipe_config import ExtractionConfig
from orchestration.resources.coingecko import CoinGeckResource


@asset(
    retry_policy=RetryPolicy(max_retries=3, delay=5),
    group_name="extraction",
    description="Raw hourly crypto prices volumes and market cap loaded into DuckDB from CoinGecko API",
)
def raw_crypto_prices(
    context: AssetExecutionContext,
    config: ExtractionConfig,
    coingecko: CoinGeckResource,
) -> Output[dict]:
    extractor = coingecko.get_extractor()

    results = extractor.extract_multiple(
        coin_ids=config.coin_id,
        vs_currency=config.vs_currency,
        days=config.days,
        rate_limit_delay=config.rate_limit_delay,
    )

    total_rows = sum(len(df) for df in results.values())

    context.log.info(f"Extracted {total_rows} rows for coins {config.coin_id}")

    return Output(
        value={"coins": config.coin_id, "total_rows": total_rows},
        metadata={
            "coin_extracted": MetadataValue.int(len(results)),
            "total_rows": MetadataValue.int(total_rows),
            "vs_currency": MetadataValue.text(config.vs_currency),
            "days": MetadataValue.int(config.days),
        },
    )
