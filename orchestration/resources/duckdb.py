import duckdb
from dagster import ConfigurableResource


class DuckdbResource(ConfigurableResource):
    db_path: str = "data/crypto.duckdb"

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(database=self.db_path)
