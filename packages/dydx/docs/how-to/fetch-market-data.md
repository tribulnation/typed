# Fetch Market Data

Use the indexer for trading-facing market data and chain modules for protocol
metadata that is committed on-chain.

```python
from dydx import Dydx

async with Dydx.testnet(public=True) as client:
  markets = await client.indexer.data.get_markets()
  btc = await client.indexer.data.get_market('BTC-USD')
  book = await client.indexer.data.get_order_book('BTC-USD')
  trades = await client.indexer.data.get_trades('BTC-USD', limit=10)
  print(markets['markets'].keys(), btc['oraclePrice'], book['bids'][:1], trades['trades'][:1])
```

For historical candles, use the indexer candle endpoint:

```python
from datetime import datetime, timezone

from dydx import Dydx

async with Dydx.testnet(public=True) as client:
  candles = await client.indexer.data.get_candles(
    'BTC-USD',
    resolution='1HOUR',
    from_iso=datetime(2026, 1, 1, tzinfo=timezone.utc),
    limit=100,
  )
  print(candles['candles'][:3])
```

For chain-native market metadata, use `client.chain`:

```python
from dydx import Dydx

async with Dydx.testnet(public=True) as client:
  clob_pair = await client.chain.clob.clob_pair(0)
  price = await client.chain.prices.market_price(0)
  print(clob_pair, price)
```
