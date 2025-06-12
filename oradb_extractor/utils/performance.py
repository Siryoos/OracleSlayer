"""Performance utilities."""

import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def timer() -> Iterator[float]:
    start = time.perf_counter()
    yield start
    end = time.perf_counter()
    print(f"Elapsed: {end - start:.4f}s")
