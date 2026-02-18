from typing import List

from dagster import Config


class ExtractionConfig(Config):
    coin_id: List[str] = ["bitcoin", "ethereum"]
    vs_currency: str = "usd"
    days: int = 7
    rate_limit_delay: float = 1.2


class VisualisationConfig(Config):
    coin_id: str = "ethereum"
    vs_currency: str = "usd"
