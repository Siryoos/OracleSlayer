"""Configuration classes for oradb-extractor."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class OracleConfig:
    """Oracle connection configuration."""

    dsn: str
    user: str
    password: str
    pool_min: int = 5
    pool_max: int = 20
    pool_increment: int = 1
    pool_timeout: int = 30
    arraysize: int = 2000
    prefetchrows: int = 2000
    stmtcachesize: int = 50
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    use_tls: bool = True
    wallet_location: Optional[str] = None

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.pool_min < 1:
            raise ValueError("pool_min must be >= 1")
        if self.pool_max < self.pool_min:
            raise ValueError("pool_max must be >= pool_min")
        if self.arraysize <= 0:
            raise ValueError("arraysize must be positive")
        if self.prefetchrows <= 0:
            raise ValueError("prefetchrows must be positive")
