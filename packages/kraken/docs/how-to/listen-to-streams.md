# Listen To Streams

`client.streams` is WebSocket v2. `streams.market_data` is public; `streams.private`
carries account channels (balances, order/trade executions) and needs credentials --
[API Keys Setup](../api-keys.md).

Every subscription returns a `StreamManager`. Use it as an async context manager, which
unsubscribes automatically on exit:

```python
from kraken import Kraken

async with Kraken.new(public=True) as client:
  async with client.streams.market_data.ticker(symbol=['BTC/USD']) as stream:
    async for message in stream:
      print(message['data'])
```

Each message is the full `{channel, type, data}` push -- `type` is `'snapshot'` for the
first message after subscribing (if you passed `snapshot=True`) and `'update'`
afterwards. `data` is a list because one subscription can cover several symbols.

## Public Channels

```python
from kraken import Kraken

async with Kraken.new(public=True) as client:
  async with client.streams.market_data.book(symbol=['BTC/USD'], depth=10) as stream:
    async for message in stream:
      print(message['data'])

  async with client.streams.market_data.trade(symbol=['BTC/USD']) as stream:
    async for message in stream:
      print(message['data'])
```

`market_data` also has `ohlc` (candle updates), `instrument` (tradable-pair/asset
metadata updates), and `status` (system status) channels, subscribed the same way.

## Private Channels

```python
from kraken import Kraken

async with Kraken.new() as client:
  async with client.streams.private.balances(snapshot=True) as stream:
    async for message in stream:
      print(message['data'])

  async with client.streams.private.executions() as stream:
    async for message in stream:
      print(message['data'])
```

`balances` streams ledger-affecting events (deposits, trades, transfers, ...);
`executions` streams order status and fills -- the single channel that replaced
WebSocket v1's separate `openOrders`/`ownTrades` channels.

## Keeping The Connection Alive

```python
from kraken import Kraken

async with Kraken.new(public=True) as client:
  await client.streams.market_data.ping()
```

Kraken closes a connection after roughly a minute of inactivity. `ping` sends an
application-level ping and returns once the server answers, useful to keep an
otherwise-idle connection open.
