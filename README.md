# oradb-extractor

High performance Oracle extraction library.

## Installation

```bash
pip install oradb-extractor
```

## Usage


```python
from oradb_extractor import extract_sync

df = extract_sync(
    "SELECT * FROM dual",
    dsn="db",
    user="u",
    password="p",
)
```

## Examples

More real-world examples can be found in the [examples](examples/) directory.


