import time
from datetime import datetime

import duckdb
import pandas as pd
import requests


class CoinGeckoExtractor:
    """
    Extract data from CoinGecko, class created due to an Airbyte bug with the connector "source-coingecko-coins"
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize DuckDB with raw data schema"""
        conn = duckdb.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_crypto_prices (
                timestamp TIMESTAMP NOT NULL,
                price DOUBLE NOT NULL,
                market_cap DOUBLE,
                total_volume DOUBLE,
                coin_id VARCHAR NOT NULL,
                vs_currency VARCHAR NOT NULL,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (timestamp, coin_id, vs_currency)
            )
        """)
        conn.close()
        print(f"Database initialized: {self.db_path}")

    def extract(self, coin_id: str, vs_currency: str, days: int) -> pd.DataFrame:
        """
        Extract market data for a cryptocurrency.

        Returns:
            DataFrame with timestamp, price, market_cap, total_volume

        Raises:
            requests.HTTPError: If API request fails
            ValueError: If no data returned
        """

        url = f"{self.BASE_URL}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days,
        }

        print(f"Extracting {days} days of {coin_id} data")

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            prices = data.get("prices", [])
            market_caps = data.get("market_caps", [])
            volumes = data.get("total_volumes", [])

            # If no prices I assume that we have no need to form a dataframe
            if not prices:
                raise ValueError(f"No data returned for {coin_id}")

            # Build DataFrame, first element is the timestamp, second the value
            df = pd.DataFrame(
                {
                    "timestamp": [datetime.fromtimestamp(p[0] / 1000) for p in prices],
                    "price": [p[1] for p in prices],
                    "market_cap": [m[1] if m else None for m in market_caps],
                    "total_volume": [v[1] if v else None for v in volumes],
                    "coin_id": coin_id,
                    "vs_currency": vs_currency,
                }
            )

            print(f"  Extracted {len(df)} records")
            print(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

            return df

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("Rate limit hit. Wait 60s and retry.")
            raise
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            raise

    def load(self, df: pd.DataFrame) -> None:
        """
        Load extracted data into DuckDB.
        Idempotent: uses INSERT OR REPLACE.
        """
        if df.empty:
            print("No data to load")
            return

        conn = duckdb.connect(self.db_path)
        try:
            conn.execute("""
                INSERT OR REPLACE INTO raw_crypto_prices
                (timestamp, price, market_cap, total_volume, coin_id, vs_currency, extracted_at)
                SELECT
                    timestamp,
                    price,
                    market_cap,
                    total_volume,
                    coin_id,
                    vs_currency,
                    CURRENT_TIMESTAMP as extracted_at
                FROM df
            """)

            # Check if the data was loaded
            params = [df["coin_id"].iloc[0], df["vs_currency"].iloc[0]]
            count = conn.execute(
                """SELECT COUNT(*) FROM raw_crypto_prices WHERE coin_id = ? AND vs_currency = ?""",
                params,
            ).fetchone()[0]

            print(
                f"Loaded to DuckDB: {count} total records for {df['coin_id'].iloc[0]}"
            )

        finally:
            conn.close()

    def extract_and_load(
        self, coin_id: str, vs_currency: str, days: int
    ) -> pd.DataFrame:
        """Extract and load in one call"""
        df = self.extract(coin_id, vs_currency, days)
        self.load(df)
        return df

    def extract_multiple(
        self,
        coin_ids: list[str],
        vs_currency: str,
        days: int,
        rate_limit_delay: float,
    ) -> dict[str, pd.DataFrame]:
        """
        Extract multiple coins with rate limiting

        Args:
            coin_ids: List of coin identifiers
            vs_currency: Target currency
            days: Days of historical data
            rate_limit_delay: Seconds between requests

        Returns:
            Dict with coin_id as key and his dataframe extracted as value
        """
        results = {}

        for i, coin_id in enumerate(coin_ids, 1):
            print(f"\n[{i}/{len(coin_ids)}] Processing {coin_id}")

            try:
                df = self.extract_and_load(coin_id, vs_currency, days)
                results[coin_id] = df

                # Sleep except when the last coin is extracted to avoid useless running time
                if i < len(coin_ids):
                    time.sleep(rate_limit_delay)

            except Exception as e:
                print(f"Skipping {coin_id}: {e}")
                continue

        print(f"\nSuccessfully processed {len(results)}/{len(coin_ids)} coins")
        return results


def main():
    extractor = CoinGeckoExtractor(db_path="data/crypto.duckdb")
    # Extract single coin
    # extractor.extract_and_load(coin_id = "bitcoin", vs_currency = "usd", days=7)

    extractor.extract_multiple(
        coin_ids=["bitcoin", "ethereum"],
        vs_currency="usd",
        days=7,
        rate_limit_delay=1.2,
    )


if __name__ == "__main__":
    main()
