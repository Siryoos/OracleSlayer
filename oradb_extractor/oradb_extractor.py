"""Core OracleExtractor implementation."""
from __future__ import annotations

import asyncio
from typing import Iterable, Optional

import oracledb
import pandas as pd

from .config import OracleConfig
from .errors import ExtractionError
from .extractors.streaming import StreamingExtractor
from .pool import AsyncPool, create_pool


class OracleExtractor:
    """High level extractor for Oracle databases."""

    def __init__(self, config: OracleConfig) -> None:
        self.config = config
        self._pool: Optional[AsyncPool] = None

    async def __aenter__(self) -> "OracleExtractor":
        await self._initialize_pool()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._cleanup()

    async def _initialize_pool(self) -> None:
        self._pool = await create_pool(self.config)

    async def _cleanup(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def extract_to_dataframe(
        self, query: str, params: Optional[Iterable] = None
    ) -> pd.DataFrame:
        if not self._pool:
            raise ExtractionError("Extractor not initialized")
        extractor = StreamingExtractor(self._pool, arraysize=self.config.arraysize)
        return await extractor.extract_to_dataframe(query, params)

    async def extract_to_parquet(
        self, query: str, output_path: str, params: Optional[Iterable] = None
    ) -> None:
        if not self._pool:
            raise ExtractionError("Extractor not initialized")
        extractor = StreamingExtractor(self._pool, arraysize=self.config.arraysize)
        await extractor.extract_to_parquet(query, output_path, params)


async def extract(
    query: str,
    dsn: str,
    user: str,
    password: str,
    **kwargs,
) -> pd.DataFrame:
    """One-line extraction convenience function."""
    config = OracleConfig(dsn=dsn, user=user, password=password)
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    async with OracleExtractor(config) as extractor:
        return await extractor.extract_to_dataframe(query)
