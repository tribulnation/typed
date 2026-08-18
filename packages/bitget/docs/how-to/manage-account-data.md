# Manage Account Data

All of these are authenticated.

## Balances

```python
from bitget import Bitget

async with Bitget.new() as client:
  assets = await client.uta.account.assets()
  print(assets['accountEquity'], assets['assets'])
```

Returns overall equity/margin metrics plus a per-coin balance list. Coins with a zero balance
are omitted.

## Account Info

```python
from bitget import Bitget

async with Bitget.new() as client:
  info = await client.uta.account.info()
  print(info['userId'], info['permType'])
```

## Financial Records

```python
from bitget import Bitget

async with Bitget.new() as client:
  records = await client.uta.account.financial_records(category='SPOT', coin='USDT')
```

Paged, see [Paginate Through Results](paginate-through-results.md).

## Positions (Futures)

```python
from bitget import Bitget

async with Bitget.new() as client:
  positions = await client.uta.position.current_positions(category='USDT-FUTURES')
  for p in positions['list'] or []:
    print(p['symbol'], p['posSide'], p['total'], p['unrealisedPnl'])

  closed = await client.uta.position.history_positions(category='USDT-FUTURES', symbol='BTCUSDT')
```

## Classic v2

```python
from bitget import Bitget

async with Bitget.new() as client:
  assets = await client.classic.spot.account_assets()
  positions = await client.classic.mix.positions(product_type='USDT-FUTURES')
```
