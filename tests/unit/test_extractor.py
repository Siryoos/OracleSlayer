import asyncio
from unittest import mock

import pytest

from oradb_extractor.config import OracleConfig
from oradb_extractor.oradb_extractor import OracleExtractor


class DummyPool:
    def __init__(self):
        self.acquire_called = False
        self.release_called = False

    async def acquire(self):
        self.acquire_called = True
        return mock.AsyncMock()

    async def release(self, conn):
        self.release_called = True

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_extract_to_dataframe(monkeypatch):
    cfg = OracleConfig(dsn="x", user="u", password="p")
    pool = DummyPool()

    async def create_pool(config):
        return pool

    monkeypatch.setattr("oradb_extractor.oradb_extractor.create_pool", create_pool)

    async with OracleExtractor(cfg) as extractor:
        with mock.patch(
            "oradb_extractor.extractors.streaming.StreamingExtractor.extract_to_dataframe",
            return_value=[{"a": 1}],
        ) as mocked:
            df = await extractor.extract_to_dataframe("SELECT 1 FROM dual")
            assert mocked.called
            assert not df is None
