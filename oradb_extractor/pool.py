"""Connection pool management."""
from __future__ import annotations

import asyncio
from typing import Optional

import oracledb

from .config import OracleConfig
from .errors import ConnectionError


class AsyncPool:
    """Async wrapper around oracledb connection pool."""

    def __init__(self, config: OracleConfig) -> None:
        self.config = config
        self._pool: Optional[oracledb.ConnectionPool] = None

    async def initialize(self) -> None:
        """Create connection pool."""
        self.config.validate()
        try:
            self._pool = await oracledb.create_pool(
                dsn=self.config.dsn,
                user=self.config.user,
                password=self.config.password,
                min=self.config.pool_min,
                max=self.config.pool_max,
                increment=self.config.pool_increment,
                timeout=self.config.pool_timeout,
                getmode=oracledb.SPOOL_ATTRVAL_WAIT,
                wait_timeout=self.config.pool_timeout,
            )
        except Exception as exc:  # pragma: no cover - thin wrapper
            raise ConnectionError(str(exc)) from exc

    async def acquire(self) -> oracledb.Connection:
        if not self._pool:
            raise ConnectionError("Pool not initialized")
        return await self._pool.acquire()

    async def release(self, connection: oracledb.Connection) -> None:
        if self._pool:
            await self._pool.release(connection)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()


async def create_pool(config: OracleConfig) -> AsyncPool:
    pool = AsyncPool(config)
    await pool.initialize()
    return pool
