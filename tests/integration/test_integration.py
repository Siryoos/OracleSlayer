import os
import pytest
from oradb_extractor import extract_sync

DSN = os.environ.get("ORACLE_DSN")
USER = os.environ.get("ORACLE_USER")
PASSWORD = os.environ.get("ORACLE_PASSWORD")

@pytest.mark.skipif(not DSN, reason="Oracle DB not configured")
def test_extract_sync():
    df = extract_sync("SELECT 1 FROM dual", dsn=DSN, user=USER, password=PASSWORD)
    assert not df.empty
