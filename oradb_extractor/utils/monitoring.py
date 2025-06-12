"""Monitoring utilities for logging and metrics."""

import logging
from typing import Optional

try:
    from opentelemetry import metrics
    from opentelemetry.sdk.metrics import MeterProvider
except Exception:  # pragma: no cover - optional dependency
    metrics = None


logger = logging.getLogger("oradb_extractor")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure default logging handler."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


def init_metrics() -> Optional[object]:
    """Initialize OpenTelemetry metrics if available."""
    if not metrics:
        return None
    provider = MeterProvider()
    metrics.set_meter_provider(provider)
    return provider.get_meter("oradb_extractor")


def log(message: str) -> None:
    logger.info(message)
