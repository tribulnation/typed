# Timestamps

Every timestamp the client returns is a timezone-aware UTC `datetime`, whatever the service
sends on the wire. Every timestamp parameter takes a `datetime`, converted to the wire
format for you.

## Wire Formats

The services use three formats; the client handles each one per field:

| Surface | On the wire |
| - | - |
| `client.trading` (REST and channels) | Epoch milliseconds |
| `client.pricing` | Epoch milliseconds |
| `client.backend` | Epoch seconds (fee and open-interest update times), ISO 8601 (`lastRefreshed`) |
| `client.backend_global` | ISO 8601 (history rows, stats dates), epoch seconds (holding rates), epoch milliseconds (contests) |

## Common Patterns

```python
from datetime import datetime, timedelta, timezone
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  now = datetime.now(timezone.utc)
  candles = await client.trading.markets.candles('BTC/USD', interval='5m', from_=now - timedelta(hours=6), to=now)
  print(candles[-1]['time'].isoformat())

  history = await client.backend_global.traders.history(
    address='0x...', chain_id=42161, start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
  )
  print(history['data'][0]['date'] if history['data'] else None)
```

Pass timezone-aware datetimes. A naive one is read differently by wire format:

- Epoch parameters (`markets.candles`' `from_` and `to`, the agent and API-key
  `timestamp`, an agent scope's `expiresAt`): your machine's local time.
- ISO 8601 parameters (`start_date` and `end_date` of `backend_global.traders.history`
  and `history_paged`): UTC.

A field the venue sets to `0` for "never" (a stake timestamp on a wallet that never staked,
for example) decodes as the Unix epoch, `1970-01-01T00:00:00+00:00`.

## Raw Helpers

`typed_gtrade.core` exports the converters the client uses, for values you handle
yourself: `timestamp_millis`, `timestamp_seconds` and `timestamp_iso`, each with `parse`
(wire value to `datetime`) and `dump` (`datetime` to wire value).

```python
from datetime import datetime, timezone
from typed_gtrade.core import timestamp_millis

now = datetime.now(timezone.utc)
wire = timestamp_millis.dump(now)    # int, epoch milliseconds; sub-millisecond digits dropped
back = timestamp_millis.parse(wire)  # a UTC datetime, to the millisecond
```

The signing builders in `typed_gtrade.signing` take a `datetime`, like the agent and
API-key methods: pass the same one to both, and the signed value and the value sent always
match. See [Wallet & Agent Setup](../authenticated-setup.md).
