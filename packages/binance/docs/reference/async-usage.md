# Async Usage

Binance clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine.

```python
from binance import Binance

client = Binance.new(public=True)
price = await client.spot.market.ticker_price(symbol='BTCUSDT')
print(price)
```

That works because each of Binance's 13 top-level surfaces (`spot`, `usdm_futures`,
`coinm_futures`, `options`, `portfolio_margin`, `streams`, `usdm_futures_streams`,
`usdm_futures_public_streams`, `coinm_futures_streams`, `options_streams`, `ws_api`,
`usdm_futures_ws_api`, `coinm_futures_ws_api`) owns its own HTTP or WebSocket transport, and
every one of those transports opens lazily on first use — nothing needs to be entered up
front.

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of
the block. Entering the top-level client is the only thing the caller does — `Binance.__aenter__`
opens all 13 sub-surfaces concurrently (via `asyncio.gather`), and you never enter a
sub-surface yourself.

```python
from binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.market.ticker_price(symbol='BTCUSDT')
  book = await client.usdm_futures.market.depth(symbol='BTCUSDT')
```

This is the recommended style for multiple requests, long-lived sessions, any streaming
workflow, or code where explicit cleanup matters.

## Streams

Each `client.streams` method (and its USD-M/COIN-M futures/options equivalents) returns a
subscription manager, not a stream directly. Use `async with` on it so the subscription is
unsubscribed automatically when the block exits:

```python
from binance import Binance

async with Binance.new(public=True) as client:
  async with client.streams.trade('BTCUSDT') as trades:
    async for trade in trades:
      print(trade['p'])
      break
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from binance import Binance

async with Binance.new(public=True) as client:
  trades = await client.streams.trade('BTCUSDT')
  async for trade in trades:
    print(trade['p'])
    break
  await trades.unsubscribe()
```

## Composite/Multi-Surface Client

`Binance.new()` bundles five product lines, each with its own REST surface and its own
subset of streaming/WS-API surfaces — none of them share a connection:

- **Spot**: REST (`client.spot`), market-data streams (`client.streams`), and a
  request/response WS API (`client.ws_api`, also used for account/order push events via
  `subscribe_user_data()`).
- **USD-M Futures**: REST (`client.usdm_futures`), two streams connections
  (`client.usdm_futures_streams` for the general channel set, plus
  `client.usdm_futures_public_streams` specifically for order-book channels, which Binance
  serves on a separate connection), and a WS API (`client.usdm_futures_ws_api`).
- **COIN-M Futures**: REST (`client.coinm_futures`), streams
  (`client.coinm_futures_streams`), and a WS API (`client.coinm_futures_ws_api`).
- **Options**: REST (`client.options`) and streams (`client.options_streams`) — Binance
  publishes no WS API for options.
- **Portfolio Margin**: REST only (`client.portfolio_margin`) — no streaming or WS API
  surface of its own.

All 13 fields are entered and exited together under one `async with Binance.new(...)`, and
every surface shares one set of credentials — Binance's HMAC signing scheme is uniform
across every REST host and the WS API.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than
one call, opening streams, or wanting predictable cleanup.
