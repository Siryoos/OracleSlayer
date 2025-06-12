import pytest
from oradb_extractor.config import OracleConfig
from oradb_extractor.oradb_extractor import OracleExtractor

@pytest.mark.asyncio
async def test_dummy_benchmark(benchmark, monkeypatch):
    cfg = OracleConfig(dsn="x", user="u", password="p")
    async def create_pool(config):
        class Dummy:
            async def acquire(self):
                return None
            async def release(self, conn):
                pass
            async def close(self):
                pass
        return Dummy()
    monkeypatch.setattr("oradb_extractor.oradb_extractor.create_pool", create_pool)
    async with OracleExtractor(cfg) as _:
        benchmark(lambda: None)
