# Timestamps

Every timestamp the client returns is a timezone-aware UTC `datetime`, and every timestamp
parameter takes a `datetime`. You never handle raw epoch numbers or ISO strings.

EVEDEX uses two wire formats, converted for you:

| Wire format | Where |
| --- | --- |
| RFC 3339 string with milliseconds (`2026-11-19T11:20:51.255Z`) | `createdAt`/`updatedAt` fields, and every request bound (`after`, `before`, `open_after`, ...) |
| Epoch milliseconds | Server time (`ping`), order-book `t`, heartbeat `t`, candle open times |

## Common Patterns

```python
from datetime import datetime, timedelta, timezone
from typed_evedex import Evedex

now = datetime.now(timezone.utc)
async with Evedex.new() as client:
  fills = await client.exchange.fills(after=now - timedelta(hours=24), before=now)
  for fill in fills['list']:
    print(fill)

  candles = await client.market_data.candles(
    instrument='BTCUSD', group='1h', after=now - timedelta(days=1), before=now
  )
  open_time = candles[0][0]  # datetime, UTC
```

A naive `datetime` is treated as UTC. Request bounds are sent with millisecond precision;
anything finer is truncated.
