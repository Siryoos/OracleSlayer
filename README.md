# oradb-extractor

High performance Oracle extraction library.

```python
from oradb_extractor import extract

df = asyncio.run(extract("SELECT * FROM dual", dsn="db", user="u", password="p"))
```
