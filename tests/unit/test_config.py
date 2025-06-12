import pytest
from oradb_extractor.config import OracleConfig


def test_validate_arraysize():
    cfg = OracleConfig(dsn="x", user="u", password="p", arraysize=0)
    with pytest.raises(ValueError):
        cfg.validate()


@pytest.mark.asyncio
async def test_create_pools(monkeypatch):
    from oradb_extractor.pool import create_pools

    async def create_pool(config):
        class Dummy:
            async def close(self):
                pass
        return Dummy()

    monkeypatch.setattr("oradb_extractor.pool.create_pool", create_pool)
    pools = await create_pools([OracleConfig(dsn="x", user="u", password="p")])
    assert len(pools) == 1
