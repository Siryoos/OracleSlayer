"""Streaming extractor implementation."""
from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

import asyncio
from ..errors import QueryError
from ..pool import AsyncPool

from .base import BaseExtractor


class StreamingExtractor(BaseExtractor):
    """Stream results in chunks."""

    def __init__(self, pool: AsyncPool, arraysize: int, prefetchrows: int) -> None:
        self.pool = pool
        self.arraysize = arraysize
        self.prefetchrows = prefetchrows

    async def execute(self, query: str, params: Optional[Iterable] = None) -> Iterable:
        conn = await self.pool.acquire()
        try:
            cursor = await asyncio.to_thread(conn.cursor)
            cursor.arraysize = self.arraysize
            cursor.prefetchrows = self.prefetchrows
            await asyncio.to_thread(cursor.execute, query, params or [])
            while True:
                rows = await asyncio.to_thread(cursor.fetchmany)
                if not rows:
                    break
                for row in rows:
                    yield row
        except Exception as exc:
            raise QueryError(str(exc)) from exc
        finally:
            await self.pool.release(conn)

    async def extract_to_dataframe(
        self, query: str, params: Optional[Iterable] = None
    ) -> pd.DataFrame:
        data = []
        async for row in self.execute(query, params):
            data.append(row)
        return pd.DataFrame(data)

    async def extract_to_parquet(
        self, query: str, output_path: str, params: Optional[Iterable] = None
    ) -> None:
        first_batch = True
        writer = None
        async for row in self.execute(query, params):
            if first_batch:
                writer = pq.ParquetWriter(
                    output_path,
                    pa.Table.from_pylist([row]).schema,
                )
                first_batch = False
            table = pa.Table.from_pylist([row])
            writer.write_table(table)
        if writer:
            writer.close()
