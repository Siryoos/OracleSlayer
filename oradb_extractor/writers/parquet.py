"""Parquet writer utilities using pyarrow."""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def to_parquet(df: pd.DataFrame, path: str) -> None:
    table = pa.Table.from_pandas(df)
    pq.write_table(table, path)
