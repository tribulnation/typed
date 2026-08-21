# Timestamps

Kraken has no single uniform timestamp convention -- it varies by endpoint rather than
following one rule (`spot.market_data.time` is the server-time *endpoint*, not a
client-side utility). Read this page before relying on any request-side time filter.

## Common Patterns

Most endpoints that filter by time take a real `datetime`, converted to the venue's own
wire shape for you; a couple take a raw string cursor instead:

- `spot.market_data.ohlc`'s `since` and `spot.market_data.spread`'s `since` are a
  `datetime` (`TimestampSeconds`), converted to Unix seconds on the wire.

  ```python
  from datetime import datetime, timedelta, timezone
  from typed_kraken import Kraken

  async with Kraken.new(public=True) as client:
    candles = await client.spot.market_data.ohlc(
      pair='XBTUSD', interval=1,
      since=datetime.now(timezone.utc) - timedelta(hours=1),
    )
  ```

- `spot.market_data.trades`'s `since` is a real `datetime` (`TimestampNanos`), converted
  to Kraken's nanosecond-epoch wire cursor for you -- pass the previous response's own
  `last` field straight through rather than computing one yourself:

  ```python
  from typed_kraken import Kraken

  async with Kraken.new(public=True) as client:
    page1 = await client.spot.market_data.trades(pair='XBTUSD')
    if cursor := page1.get('last'):
      page2 = await client.spot.market_data.trades(pair='XBTUSD', since=cursor)
  ```

  Python's `datetime` only carries microsecond precision, so round-tripping `last`
  through a `datetime` and back loses the sub-microsecond tail of Kraken's nanosecond
  cursor (confirmed: `1786622308334567536` round-trips to `1786622308334567168`) -- the
  round-tripped value is not byte-identical to what Kraken originally sent, though still
  within the same microsecond.

- Response timestamp fields validated by the client (e.g.
  `spot.market_data.post_trade`'s `last_ts`/`trade_ts`/`publication_ts`, or
  `streams.market_data.ticker`'s wire-level `timestamp` string) come back as documented in
  their own `TypedDict`. Where a field is typed `datetime`, `pydantic` parses Kraken's
  RFC3339 response strings into a real `datetime` for you automatically -- this direction is
  confirmed working.

## `post_trade`'s `from_ts`/`to_ts`

`spot.market_data.post_trade` types its `from_ts`/`to_ts` parameters as native `datetime`
and serializes them to Kraken's required RFC3339 wire format (`"2024-05-30T12:34:56.123456789Z"`)
before they reach the request's query parameters -- pass a `datetime` directly, timezone-aware
or naive (naive values are treated as UTC):

```python
from datetime import datetime, timezone
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  page = await client.spot.market_data.post_trade(
    symbol='BTC/USD', from_ts=datetime(2024, 5, 30, tzinfo=timezone.utc),
  )
```

Verified live against the real API: Kraken's own filtering now works correctly -- a `from_ts`
set to a future timestamp is no longer silently ignored, and Kraken genuinely returns
`{'last_ts': '', 'count': 0, 'trades': []}` for it instead of its unfiltered default recent
trades. That specific empty-result payload, however, currently fails to *validate* under this
client's default `validate=True`: Kraken sends `last_ts` back as a literal `''` rather than
omitting it, and `''` doesn't parse as a timestamp, so a `from_ts`/`to_ts` window with zero
matching trades raises a `pydantic.ValidationError` instead of returning cleanly -- a
separate, tracked issue, not a regression of the filtering fix above.

`spot.market_data.pre_trade` takes only `symbol` today -- it has no time-range parameters at
all, native `datetime` or otherwise.
