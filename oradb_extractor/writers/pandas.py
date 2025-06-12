"""DataFrame writer utilities."""

import pandas as pd


def to_dataframe(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)
