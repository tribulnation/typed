# Timestamps

Kraken has **no dedicated timestamp helper module** -- there is no `now()`/`dump()`/`parse()`
exported anywhere in the package (`spot.market_data.time` is the server-time *endpoint*, not
a client-side utility). The timestamp convention genuinely varies by endpoint rather than
following one rule, and one corner of it is a confirmed, unfixed bug rather than just an
inconsistency -- read this page before relying on any request-side time filter.

## Common Patterns

Most endpoints that filter by time take a raw integer or string cursor, not a `datetime`:

- `spot.market_data.ohlc`'s `since` and `spot.market_data.spread`'s `since` are plain
  `int` Unix seconds.

  ```python
  import time
  from kraken import Kraken

  async with Kraken.new(public=True) as client:
    candles = await client.spot.market_data.ohlc(
      pair='XBTUSD', interval=1, since=int(time.time()) - 3600,
    )
  ```

- `spot.market_data.trades`'s `since` is a `str` nanosecond cursor (the previous
  response's own `last` field, not something you compute):

  ```python
  from kraken import Kraken

  async with Kraken.new(public=True) as client:
    page1 = await client.spot.market_data.trades(pair='XBTUSD')
    if cursor := page1.get('last'):
      page2 = await client.spot.market_data.trades(pair='XBTUSD', since=cursor)
  ```

- Response timestamp fields validated by the client (e.g.
  `spot.market_data.post_trade`'s `last_ts`/`trade_ts`/`publication_ts`, or
  `streams.market_data.ticker`'s wire-level `timestamp` string) come back as documented in
  their own `TypedDict`. Where a field is typed `datetime`, `pydantic` parses Kraken's
  RFC3339 response strings into a real `datetime` for you automatically -- this direction is
  confirmed working.

## Known Issue: `post_trade`'s `from_ts`/`to_ts` do not filter correctly

`spot.market_data.post_trade` types its `from_ts`/`to_ts` parameters as native `datetime`
and passes them straight into the request's query `params` dict -- there is no
serialization step anywhere in the chain down through `HttpRpcClient.request` to the
underlying `httpx` call. Kraken's own spec for this endpoint requires RFC3339
(`"2024-05-30T12:34:56.123456789Z"`), but `httpx` stringifies a non-primitive query
parameter with plain `str()`, which for a `datetime` produces
`"2024-05-30 12:34:56.123456+00:00"` (a space instead of `T`, no trailing `Z`, and this
package never even attaches a timezone unless you pass a timezone-aware `datetime`
yourself).

This was verified live against the real API rather than assumed: sending a
correctly-formatted RFC3339 `from_ts` set to a future timestamp returns an empty result
(`{"count": 0, "trades": []}`), confirming Kraken filters when it can parse the value. Sending
the exact same future timestamp through this package's `from_ts=datetime(...)` -- i.e. the
malformed `str(datetime)` format -- returns Kraken's *default*, unfiltered set of recent
trades instead, with `"error": []` and a `200` status. **Kraken silently fails to parse the
malformed value and falls back to ignoring the filter, rather than rejecting the request.**
So today, `post_trade(from_ts=..., to_ts=...)` does not filter by time at all -- it looks
like it works (no exception, a valid-looking response) but silently returns the wrong data.

This is a real client bug, not just a docs gap. Until it's fixed in `post_trade.py` (e.g. by
formatting `from_ts`/`to_ts` as RFC3339 before they reach `params`), don't rely on
`post_trade`'s `from_ts`/`to_ts` for filtering -- use `count` and post-filter the returned
`trades` client-side instead if you need a bounded window.

`spot.market_data.pre_trade` takes only `symbol` today -- it has no time-range parameters at
all, native `datetime` or otherwise.
