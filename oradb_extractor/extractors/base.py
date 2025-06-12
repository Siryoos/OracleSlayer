"""Abstract base extractor."""
from __future__ import annotations

import abc
from typing import Iterable, Optional

import pandas as pd


class BaseExtractor(abc.ABC):
    """Base extractor interface."""

    @abc.abstractmethod
    async def execute(self, query: str, params: Optional[Iterable] = None) -> Iterable:
        """Execute a query and yield rows."""

    @abc.abstractmethod
    async def extract_to_dataframe(
        self, query: str, params: Optional[Iterable] = None
    ) -> pd.DataFrame:
        """Return query results as DataFrame."""
