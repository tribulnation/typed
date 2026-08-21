# Timestamps

Timestamps work differently on dYdX's two sides. This page covers the indexer's `datetime`
convention -- the chain/gRPC side is a genuinely different mechanism and isn't covered here.

## Indexer: Native `datetime`

Indexer endpoints that take a timestamp accept a Python `datetime` directly, and validated
response fields come back as `datetime` too -- there's nothing to convert by hand.

```python
from datetime import datetime, timezone

from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  candles = await client.indexer.data.get_candles(
    'BTC-USD',
    resolution='1HOUR',
    from_iso=datetime(2026, 1, 1, tzinfo=timezone.utc),
    limit=100,
  )
  print(candles['candles'][0]['startedAt'])  # already a datetime
```

## Common Patterns

Pass a `datetime` directly wherever an indexer endpoint takes a time window -- fills,
transfers, funding payments, historical PnL, and candles all follow this convention.

```python
from datetime import datetime, timedelta

end = datetime.now()
start = end - timedelta(hours=1)
```

## Raw Helpers

`dydx.indexer.timestamp` exports a single helper, `dump(value: datetime) -> str`, which
serializes a `datetime` into the ISO-8601-with-`Z` string the indexer's query parameters
expect. Every indexer endpoint that takes a timestamp already calls this internally -- you
only need it yourself if you're building a raw request outside the generated methods.

```python
from datetime import datetime

from typed_dydx.indexer import timestamp as ts

wire_value = ts.dump(datetime.now())
```

Unlike some other Typed clients' timestamp modules, there is no `now()` or `parse()`
exported here -- just `dump()`. There's no need for a `parse()` counterpart: response
fields are already typed and validated as `datetime`, not returned as raw strings.

## Chain (gRPC / Comet): Proto-Native, Not This Convention

`client.chain` does not use the indexer's `ts.dump()` convention at all. gRPC responses
carry `datetime` fields generated directly from `google.protobuf.Timestamp` by the proto
bindings (for example `Header.time`), and Comet HTTP responses parse RFC3339 timestamps
into `datetime` the same way. Neither side exposes a `dump`/`parse` helper, and chain-side
queries are addressed by block height or transaction hash, not by a timestamp request
parameter -- so there's no request-side conversion step to document here.
