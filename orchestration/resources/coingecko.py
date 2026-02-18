from dagster import ConfigurableResource

from extraction.extract_crypto import CoinGeckoExtractor


class CoinGeckResource(ConfigurableResource):
    db_path: str = "data/crypto.duckdb"
    interval: float = 1.2

    def get_extractor(self) -> CoinGeckoExtractor:
        return CoinGeckoExtractor(db_path=self.db_path)
