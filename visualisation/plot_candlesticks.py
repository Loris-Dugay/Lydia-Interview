import duckdb
import mplfinance as mpf
import pandas as pd
from duckdb import DuckDBPyConnection


def plot_candlesticks(
    conn: DuckDBPyConnection, coin_id: str = "ethereum", vs_currency: str = "usd"
):
    df = conn.execute(
        "SELECT * FROM daily_candlesticks WHERE coin_id = ? AND vs_currency = ? ORDER BY price_date",
        [coin_id, vs_currency],
    ).df()

    ohlc = pd.DataFrame(
        {
            "Open": df["open"],
            "High": df["higher"],
            "Low": df["lower"],
            "Close": df["close"],
        }
    )
    ohlc.index = pd.DatetimeIndex(df["price_date"])

    mpf.plot(
        ohlc,
        type="candle",
        style="yahoo",
        figsize=(14, 7),
        title=f"{coin_id.capitalize()} - Daily Candlesticks ({vs_currency.upper()})",
        ylabel=f"Price ({vs_currency.upper()})",
        volume=False,
    )


if __name__ == "__main__":
    conn = duckdb.connect("data/crypto.duckdb", read_only=True)
    plot_candlesticks(conn=conn)
    conn.close()
