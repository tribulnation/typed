# Async Usage

Deribit clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine.

```python
from typed_deribit import Deribit

client = Deribit.new(public=True)
ticker = await client.http.market_data.ticker(instrument_name='BTC-PERPETUAL')
print(ticker['last_price'])
```

That works because `.http`, `.ws`, and `.streams` are each a `cached_property` — the
underlying transport opens lazily on first use, not at construction.

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of
the block.

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  instruments = await client.http.market_data.get_instruments(
    currency='BTC', kind='future'
  )
  summary = await client.http.account.get_account_summary(currency='BTC')
```

`Deribit.new(...)` connects nothing by itself — entering the top-level client via
`async with` is the only thing the caller does. `.http`, `.ws`, and `.streams` open their
own transports lazily as each is first used; there's no separate sub-client to enter.
Entering the top-level client does eagerly call `__aenter__` on all three at once (so they're
already open the moment the block starts, rather than on first call), but that's still one
`async with`, never three.

This is the recommended style for:

- multiple requests in the same flow
- long-lived sessions
- any streaming workflow
- code where explicit cleanup matters

## Streams

`client.streams` subscribes to Deribit's channel push feed, always over its own dedicated
WebSocket connection, independent of `.ws`. It fans into `market_data` (public channels —
tickers, order books, trades, ...), `user` (private `user.*` channels, need credentials),
`block_rfq`, and a raw `rpc` escape hatch for any JSON-RPC method not otherwise covered.

Use `async with` on the returned subscription so it unsubscribes automatically when the
block exits:

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  async with client.streams.market_data.ticker('BTC-PERPETUAL', 'raw') as ticks:
    async for tick in ticks:
      print(tick['last_price'])
```

`await`ing the subscription directly also works, but leaves it open until you call
`unsubscribe()` yourself:

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  ticks = await client.streams.market_data.ticker('BTC-PERPETUAL', 'raw')
  async for tick in ticks:
    print(tick['last_price'])
    break
  await ticks.unsubscribe()
```

Private channels (`client.streams.user.*`) need credentials and raise `AuthError` lazily,
once the subscription actually connects, if the client has none.

## Composite/Multi-Surface Client

`Deribit.new(...)` bundles three independent transports:

- `.http` — request/reply over HTTP.
- `.ws` — the same request/reply surface over WebSocket, plus a handful of methods Deribit
  only serves this way (`trading.mass_quote`, `session.set_heartbeat`, ...).
- `.streams` — channel subscriptions, always WebSocket, on its own connection separate
  from `.ws`.

`.http` and `.ws` expose the identical method surface — `market_data`, `trading`, `account`,
`auth`, `block_rfq`, `block_trade`, `combo_books`, `matching_engine`, `session`,
`subscription_management`, `supporting` — call whichever transport fits; they're two
separate connections, not aliases for one.

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  via_http = await client.http.market_data.ticker(instrument_name='BTC-PERPETUAL')
  via_ws = await client.ws.market_data.ticker(instrument_name='BTC-PERPETUAL')
```

All three (`.http`, `.ws`, `.streams`) are entered and exited together under one top-level
`async with Deribit.new(...)`.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than
one call, opening streams, or wanting predictable cleanup.
