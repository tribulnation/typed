# Async Usage

Deribit clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine.

```python
from typed_deribit import Deribit

client = Deribit.new(public=True)
ticker = await client.market_data.ticker(instrument_name='BTC-PERPETUAL')
print(ticker['last_price'])
```

That works because every section (`market_data`, `trading`, `streams`, ...) is a
`cached_property` — the underlying transport opens lazily on first use, not at
construction.

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of
the block.

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  instruments = await client.market_data.get_instruments(
    currency='BTC', kind='future'
  )
  summary = await client.account.get_account_summary(currency='BTC')
```

`Deribit.new(...)` connects nothing by itself — entering the top-level client via
`async with` is the only thing the caller does. Every section opens its own transport
lazily as it's first used; there's no separate sub-client to enter. Entering the top-level
client does eagerly call `__aenter__` on both underlying connections at once (so they're
already open the moment the block starts, rather than on first call), but that's still one
`async with`, never several.

This is the recommended style for:

- multiple requests in the same flow
- long-lived sessions
- any streaming workflow
- code where explicit cleanup matters

## Streams

`client.streams` subscribes to Deribit's channel push feed, always over its own dedicated
WebSocket connection. It fans into `market_data` (public channels — tickers, order books,
trades, ...), `user` (private `user.*` channels, need credentials), and `block_rfq`.

Use `async with` on the returned subscription so it unsubscribes automatically when the
block exits:

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  async with client.streams.market_data.ticker('BTC-PERPETUAL', interval='raw') as ticks:
    async for tick in ticks:
      print(tick['last_price'])
```

`await`ing the subscription directly also works, but leaves it open until you call
`unsubscribe()` yourself:

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  ticks = await client.streams.market_data.ticker('BTC-PERPETUAL', interval='raw')
  async for tick in ticks:
    print(tick['last_price'])
    break
  await ticks.unsubscribe()
```

Private channels (`client.streams.user.*`) need credentials and raise `AuthError` lazily,
once the subscription actually connects, if the client has none.

## Transport

`Deribit.new(...)` bundles two independent connections: an HTTP connection and a shared
WebSocket connection. Every request/reply method — `market_data`, `trading`, `account`,
`auth`, `block_rfq`, `block_trade`, `combo_books`, `matching_engine`, `session`,
`subscription_management`, `supporting` — is reachable through one call site, with a
per-call `transport` keyword picking the connection: `'http'` (the default) or `'ws'`.
`client.streams` is a third connection again, dedicated to channel subscriptions.

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  via_http = await client.market_data.ticker(instrument_name='BTC-PERPETUAL')
  via_ws = await client.market_data.ticker(instrument_name='BTC-PERPETUAL', transport='ws')
```

A handful of methods Deribit only ever serves over WebSocket (`trading.mass_quote`,
`session.set_heartbeat`, ...) take no `transport` keyword at all — there's nothing to
choose, so the call always goes out over the WebSocket connection.

All three underlying connections (HTTP, WebSocket, and the dedicated streams socket) are
entered and exited together under one top-level `async with Deribit.new(...)`.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than
one call, opening streams, or wanting predictable cleanup.
