from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from extraction.extract_crypto import CoinGeckoExtractor


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def extractor(tmp_path):
    """CoinGeckoExtractor with a temporary DuckDB database."""
    return CoinGeckoExtractor(db_path=str(tmp_path / "test.duckdb"))


@pytest.fixture
def mock_api_response():
    """Fake CoinGecko API response — no real HTTP call made."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "prices": [[1704067200000, 42000.0], [1704153600000, 43000.0]],
        "market_caps": [[1704067200000, 800_000_000.0], [1704153600000, 810_000_000.0]],
        "total_volumes": [[1704067200000, 20_000_000.0], [1704153600000, 21_000_000.0]],
    }
    return mock_response


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_database_initialisation(extractor):
    """Table raw_crypto_prices should exist after extractor is created."""
    import duckdb
    conn = duckdb.connect(extractor.db_path)
    tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
    conn.close()
    assert "raw_crypto_prices" in tables


def test_extract_returns_correct_schema(extractor, mock_api_response):
    """extract() should return a DataFrame with the expected columns and types."""
    with patch("requests.get", return_value=mock_api_response):
        df = extractor.extract(coin_id="bitcoin", vs_currency="usd", days=1)
    assert isinstance(df, pd.DataFrame)
    assert {"timestamp", "price", "coin_id", "vs_currency"}.issubset(df.columns)
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert pd.api.types.is_float_dtype(df["price"])


def test_load_is_idempotent(extractor, mock_api_response):
    """Loading the same data twice should not create duplicates."""
    with patch("requests.get", return_value=mock_api_response):
        df = extractor.extract(coin_id="bitcoin", vs_currency="usd", days=1)
    extractor.load(df)
    extractor.load(df)
    import duckdb
    conn = duckdb.connect(extractor.db_path)
    count = conn.execute("SELECT COUNT(*) FROM raw_crypto_prices").fetchone()[0]
    conn.close()
    assert count == len(df)


def test_api_is_reachable():
    """CoinGecko API should respond — 200 OK or 429 rate limit both prove connectivity."""
    response = requests.get(f"{CoinGeckoExtractor.BASE_URL}/ping", timeout=10)
    assert response.status_code in (200, 429)


def test_extract_invalid_coin_raises(extractor):
    """Requesting an unknown coin should raise an HTTPError."""
    with pytest.raises(requests.exceptions.HTTPError):
        extractor.extract(coin_id="this-coin-does-not-exist", vs_currency="usd", days=1)
