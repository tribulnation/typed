# Async Usage

Binance clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine.

```python
from typed_binance import Binance

client = Binance.new(public=True)
price = await client.spot.http.market.ticker_price(symbol='BTCUSDT')
print(price)
```

That works because each of Binance's five products (`spot`, `usdm_futures`, `coinm_futures`,
`options`, `portfolio_margin`) groups its own transports (`http`, and a product-specific
subset of `streams`/`public_streams`/`private_streams`/`ws`, 16 transports in total) as
sibling fields, and every one of those transports opens lazily on first use — nothing needs
to be entered up front.

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of
the block. Entering the top-level client is the only thing the caller does — `Binance.__aenter__`
opens all five products concurrently (via `asyncio.gather`), each of which in turn opens its
own transports concurrently, and you never enter a product or transport yourself.

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.http.market.ticker_price(symbol='BTCUSDT')
  book = await client.usdm_futures.http.market.depth(symbol='BTCUSDT')
```

This is the recommended style for multiple requests, long-lived sessions, any streaming
workflow, or code where explicit cleanup matters.

## Streams

Each `client.spot.streams` method (and its USD-M/COIN-M futures/options equivalents) returns
a subscription manager, not a stream directly. Use `async with` on it so the subscription is
unsubscribed automatically when the block exits:

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  async with client.spot.streams.trade('BTCUSDT') as trades:
    async for trade in trades:
      print(trade['p'])
      break
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  trades = await client.spot.streams.trade('BTCUSDT')
  async for trade in trades:
    print(trade['p'])
    break
  await trades.unsubscribe()
```

## Composite/Multi-Surface Client

`Binance.new()` bundles five product lines, each a nested composite of its own REST surface
(`http`) and its own subset of streaming/WS-API transports — none of them share a
connection:

- **Spot**: REST (`client.spot.http`), market-data streams (`client.spot.streams`), and a
  request/response WS API (`client.spot.ws`, also used for account/order push events via
  `subscribe_user_data()`).
- **USD-M Futures**: REST (`client.usdm_futures.http`), two market-data streams connections
  (`client.usdm_futures.streams` for the general channel set, plus
  `client.usdm_futures.public_streams` specifically for order-book channels, which Binance
  serves on a separate connection), the private user-data stream
  (`client.usdm_futures.private_streams`), and a WS API (`client.usdm_futures.ws`).
- **COIN-M Futures**: REST (`client.coinm_futures.http`), streams
  (`client.coinm_futures.streams`), and a WS API (`client.coinm_futures.ws`). COIN-M has no
  private user-data stream yet.
- **Options**: REST (`client.options.http`), streams (`client.options.streams`), and the
  private user-data stream (`client.options.private_streams`) — Binance publishes no WS API
  for options.
- **Portfolio Margin**: REST (`client.portfolio_margin.http`) and the private user-data
  stream (`client.portfolio_margin.private_streams`) — no public streaming or WS API surface
  of its own.

All five products (and every transport nested under them) are entered and exited together
under one `async with Binance.new(...)`, and every surface shares one set of credentials —
Binance's HMAC signing scheme is uniform across every REST host and the WS API.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than
one call, opening streams, or wanting predictable cleanup.
