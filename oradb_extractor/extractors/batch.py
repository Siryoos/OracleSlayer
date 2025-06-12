"""Batch extractor using fetchall (not memory efficient)."""
from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ..errors import QueryError
from ..pool import AsyncPool

from .base import BaseExtractor


class BatchExtractor(BaseExtractor):
    """Fetch all rows at once."""

    def __init__(self, pool: AsyncPool) -> None:
        self.pool = pool

    async def execute(self, query: str, params: Optional[Iterable] = None) -> Iterable:
        conn = await self.pool.acquire()
        try:
            cursor = await conn.cursor()
            await cursor.execute(query, params or [])
            rows = await cursor.fetchall()
            for row in rows:
                yield row
        except Exception as exc:
            raise QueryError(str(exc)) from exc
        finally:
            await self.pool.release(conn)

    async def extract_to_dataframe(
        self, query: str, params: Optional[Iterable] = None
    ) -> pd.DataFrame:
        return pd.DataFrame([row async for row in self.execute(query, params)])

    async def extract_to_parquet(
        self, query: str, output_path: str, params: Optional[Iterable] = None
    ) -> None:
        table = pa.Table.from_pandas(await self.extract_to_dataframe(query, params))
        pq.write_table(table, output_path)
