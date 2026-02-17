from datetime import datetime, timedelta

import airbyte as ab
import duckdb


# def extract_crypto_data(
#     coin_id: str = "bitcoin", days: str = "1", output_db: str = "data/crypto.duckdb"
# ) -> None:
#     """
#     Extract crypto price data using PyAirbyte.

#     Think of this as the "data collector" - it fetches raw data
#     from CoinGecko and drops it into DuckDB without any transformation.
#     """
# source = ab.get_source(
#     "source-coingecko-coins",
#     config={
#         "coin_id": "bitcoin",
#         "vs_currency": "usd",
#         "days": "1",
#         "start_date": "01-01-2026",
#         "end_date": "02-01-2026",
#     },
# )

# print(source.get_config())

# source.check()
# source.get_available_streams()
# source.select_all_streams()

# cache = ab.get_default_cache()
# result = source.read(cache=cache)

# conn = duckdb.connect(output_db)

# for stream_name, records in result.streams.items():
#     df = records.to_pandas()

#     # Create raw table
#     conn.execute(f"""
#         CREATE TABLE IF NOT EXISTS raw_crypto_prices (
#             timestamp TIMESTAMP,
#             price DOUBLE,
#             market_cap DOUBLE,
#             total_volume DOUBLE,
#             coin_id VARCHAR,
#             extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     # Insert data (idempotent: check for duplicates)
#     conn.execute("""
#         INSERT INTO raw_crypto_prices
#         SELECT * FROM df
#         WHERE NOT EXISTS (
#             SELECT 1 FROM raw_crypto_prices rcp
#             WHERE rcp.timestamp = df.timestamp
#             AND rcp.coin_id = df.coin_id
#         )
#     """)

# conn.close()
# print(f"✓ Extracted {len(df)} records for {coin_id}")


# if __name__ == "__main__":
#     extract_crypto_data()
