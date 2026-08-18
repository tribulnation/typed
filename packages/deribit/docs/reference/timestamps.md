# Timestamps

Deribit takes and returns raw millisecond-epoch integers everywhere, uniformly across
`.http`, `.ws`, and `.streams` — there's no `datetime` conversion on the request or response
side. The core (`deribit.core.types`) does define a `Timestamp` alias
(`EpochConverter.milliseconds`, UTC) for pydantic validation, but nothing in the generated
surface actually uses it as a field or parameter type: every documented timestamp is plain
`int`. Treat that alias as an internal implementation detail, not something to import or
call.

## Common Patterns

Windowed requests take `int` milliseconds directly:

```python
from deribit import Deribit

async with Deribit.new(public=True) as client:
  history = await client.http.market_data.get_funding_rate_history(
    instrument_name='BTC-PERPETUAL',
    start_timestamp=1_700_000_000_000,
    end_timestamp=1_700_003_600_000,
  )
```

Response timestamp fields (`Ticker.timestamp`, `BookSummaryItem.creation_timestamp`, order
and trade timestamps, ...) come back as `int` milliseconds too, with no conversion applied.

Convert to or from a Python `datetime` yourself when you need one:

```python
from datetime import datetime, timezone

now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
as_datetime = datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc)
```
