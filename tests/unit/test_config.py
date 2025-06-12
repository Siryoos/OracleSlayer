import pytest
from oradb_extractor.config import OracleConfig


def test_validate_arraysize():
    cfg = OracleConfig(dsn="x", user="u", password="p", arraysize=0)
    with pytest.raises(ValueError):
        cfg.validate()
