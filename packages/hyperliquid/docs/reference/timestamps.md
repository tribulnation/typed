# Timestamps

Many Hyperliquid methods expect UTC timestamps in milliseconds.

Use the helper exported by the client:

```python
from hyperliquid.core import timestamp as ts
```

## Common Patterns

Use `ts.now()` when you want the current time in milliseconds.

```python
from hyperliquid.core import timestamp as ts

end_time = ts.now()
```

Use `ts.dump(...)` when you have a Python `datetime` and need to convert it into Hyperliquid's millisecond format.

```python
from datetime import datetime, timedelta
from hyperliquid.core import timestamp as ts

start_time = ts.dump(datetime.now() - timedelta(hours=1))
```

Together:

```python
from datetime import datetime, timedelta
from hyperliquid.core import timestamp as ts

end_time = ts.now()
start_time = ts.dump(datetime.now() - timedelta(hours=1))
```
