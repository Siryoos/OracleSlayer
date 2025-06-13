"""Connection pool management."""
from __future__ import annotations

import asyncio
from typing import Iterable, List, Optional

import cx_Oracle

from .config import OracleConfig
from .errors import ConnectionError
from .utils.monitoring import init_metrics


class AsyncPool:
    """Async wrapper around cx_Oracle session pool."""

    def __init__(self, config: OracleConfig) -> None:
        self.config = config
        self._pool: Optional[cx_Oracle.SessionPool] = None
        self._failure_count = 0
        self._circuit_open = False
        self._meter = init_metrics()
        self._connections_gauge = None

    async def initialize(self) -> None:
        """Create connection pool."""
        self.config.validate()
        try:
            self._pool = await asyncio.to_thread(
                cx_Oracle.SessionPool,
                user=self.config.user,
                password=self.config.password,
                dsn=self.config.dsn,
                min=self.config.pool_min,
                max=self.config.pool_max,
                increment=self.config.pool_increment,
                timeout=self.config.pool_timeout,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT,
                threaded=True,
                stmtcachesize=self.config.stmtcachesize,
            )
            if self._meter:
                self._connections_gauge = self._meter.create_observable_gauge(
                    "open_connections",
                    lambda result: result.observe(getattr(self._pool, "opened", 0)),
                )
        except Exception as exc:  # pragma: no cover - thin wrapper
            raise ConnectionError(str(exc)) from exc

    async def acquire(self) -> cx_Oracle.Connection:
        if self._circuit_open:
            raise ConnectionError("Connection circuit open")
        if not self._pool:
            raise ConnectionError("Pool not initialized")
        delay = self.config.retry_delay
        for attempt in range(self.config.max_retries):
            try:
                conn = await asyncio.to_thread(self._pool.acquire)
                self._failure_count = 0
                return conn
            except Exception as exc:  # pragma: no cover - thin wrapper
                self._failure_count += 1
                if attempt == self.config.max_retries - 1:
                    self._circuit_open = True
                    raise ConnectionError(str(exc)) from exc
                await asyncio.sleep(delay)
                delay *= self.config.retry_backoff

    async def release(self, connection: cx_Oracle.Connection) -> None:
        if self._pool:
            await asyncio.to_thread(self._pool.release, connection)

    async def get_stats(self) -> dict:
        if not self._pool:
            return {}
        return {
            "open": getattr(self._pool, "opened", None),
            "busy": getattr(self._pool, "busy", None),
        }

    def reset_circuit(self) -> None:
        self._failure_count = 0
        self._circuit_open = False

    async def close(self) -> None:
        if self._pool:
            await asyncio.to_thread(self._pool.close)


async def create_pool(config: OracleConfig) -> AsyncPool:
    pool = AsyncPool(config)
    await pool.initialize()
    return pool


async def create_pools(configs: Iterable[OracleConfig]) -> List[AsyncPool]:
    pools: List[AsyncPool] = []
    async def _create(cfg: OracleConfig) -> None:
        pool = await create_pool(cfg)
        pools.append(pool)

    if hasattr(asyncio, "TaskGroup"):
        async with asyncio.TaskGroup() as tg:
            for cfg in configs:
                tg.create_task(_create(cfg))
    else:
        await asyncio.gather(*[_create(cfg) for cfg in configs])
    return pools
