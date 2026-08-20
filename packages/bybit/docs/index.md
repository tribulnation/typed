# Typed Bybit

> A fully typed, validated async client for the Bybit v5 API.

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  ticker = await client.http.market.tickers(category='spot', symbol='BTCUSDT')
  print(ticker['list'][0]['lastPrice'])
```

## Why Typed Bybit?

- **🎯 Precise Types**: Typed inputs and responses across REST and WebSocket, discriminated by product category, for trading, positions, account, assets, and earn products alike.
- **✅ Runtime Validation**: Responses and pushed stream messages validated by default.
- **⚡ Async First**: One shared HTTP pool and nine lazily-opened WebSocket connections, built for concurrent workflows.
- **📚 Full Surface**: Nearly the entire documented v5 REST and WebSocket surface — market data, order entry, positions, account, assets, earn, and more.

## Installation

```bash
pip install typed-bybit
```

## The Client

`Bybit` reaches every HTTP endpoint under `client.http` and every WebSocket connection under
`client.ws` from one object:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  candles = await client.http.market.kline(category='spot', symbol='BTCUSDT', interval='60', limit=3)
  book = await client.http.market.orderbook(category='spot', symbol='BTCUSDT', limit=5)
  trades = await client.http.market.recent_trades(category='spot', symbol='BTCUSDT', limit=3)
  print(candles['list'][0], book['b'][0], trades['list'][0]['price'])
```

`client.http.market` covers the public REST Market surface. Everything else under
`client.http` — `trade`, `position`, `account`, `asset`, `finance` and the rest — needs
credentials, as do `client.ws.private` and `client.ws.trade`. `client.ws.spot`, `.linear`,
`.inverse`, `.option`, `.spread`, `.rfq`, and `.finance` are the public-category WebSocket
streams. See [API Keys Setup](api-keys.md) for credentials and
[Async Usage](reference/async-usage.md) for the full transport layout.

## How To

- [Fetch Candles](how-to/fetch-candles.md)
- [Read The Order Book](how-to/read-the-order-book.md)
- [List Instruments](how-to/list-instruments.md)
- [Read Tickers And Trades](how-to/read-tickers.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Manage Deposits & Withdrawals](how-to/manage-deposits-withdrawals.md)
- [Manage Earn Instruments](how-to/manage-earn-instruments.md)
- [Paginate Through Results](how-to/paginate-through-results.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Configuration](reference/configuration.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Bybit follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
