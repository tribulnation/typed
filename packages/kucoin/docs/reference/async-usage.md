# Async Usage

KuCoin clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine — every underlying transport
opens lazily on first use.

```python
from kucoin import KuCoin

client = KuCoin.new(public=True)
ticker = await client.spot.ticker(symbol='BTC-USDT')
print(ticker['price'])
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of
the block.

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  ticker = await client.spot.ticker(symbol='BTC-USDT')
  book = await client.spot.part_orderbook('20', symbol='BTC-USDT')
```

`async with KuCoin.new(...)` is the only thing you need — every product underneath
(`client.spot`, `client.account`, `client.streams`, ...) enters lazily as it's first used.
You never enter a sub-client yourself.

This is the recommended style for:

- multiple requests in the same flow
- long-lived sessions
- any streaming workflow
- code where explicit cleanup matters

## Streams

`client.streams.spot_margin` is one physical WebSocket connection carrying both public
topics (order book, ticker, trades, ...) and, once the client has credentials, private
topics (balance updates, order updates, ...). Each subscription method returns a manager,
not a stream directly.

Use `async with` on it so the subscription is unsubscribed automatically when the block exits:

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  async with client.streams.spot_margin.ticker('BTC-USDT') as stream:
    async for update in stream:
      print(update['price'])
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  stream = await client.streams.spot_margin.ticker('BTC-USDT')
  async for update in stream:
    print(update['price'])
    break
  await stream.unsubscribe()
```

Private topics work the same way, against a client built with real credentials:

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  async with client.streams.spot_margin.balance() as stream:
    async for update in stream:
      print(update['currency'], update['available'])
```

**`client.streams.futures` is not usable yet.** The connection itself opens the same way as
`spot_margin`, but no channel (ticker, order book, private order/position updates, ...) is
wired onto it — there is currently no method to subscribe to. Futures market data and
account updates need polling the REST `client.futures` surface instead, until futures
streaming channels are added.

## Composite/Multi-Surface Client

`KuCoin.new()` bundles ten REST product groups plus streaming behind one object:
`client.account`, `client.spot`, `client.margin`, `client.earn`, `client.vip_lending`,
`client.affiliate`, `client.convert`, `client.futures`, `client.copy_trading`,
`client.broker`, and `client.streams`.

The ten REST products share exactly three HTTP clients, by base URL:

- `api.kucoin.com` — `account`, `spot`, `margin`, `earn`, `vip_lending`, `affiliate`, `convert`
- `api-futures.kucoin.com` — `futures`, `copy_trading`
- `api-broker.kucoin.com` — `broker`

Every product on the same host shares one connection pool, rather than each opening its own.

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  spot_balances = await client.account.spot_accounts()
  positions = await client.futures.positions.get_position_list()
```

`client.streams.spot_margin` and `client.streams.futures` are two independent WebSocket
connections, each with its own bullet-token endpoint — they don't share a base URL with
each other or with the REST clients above.

## Guidance

Use direct construction for quick reads.

Use `async with` by default when:

- you are doing more than one call
- you are opening streams
- you want predictable cleanup
