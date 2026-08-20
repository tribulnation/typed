# Fetch Account Data

These calls are signed — see [API Keys Setup](../api-keys.md).

## Balances

```python
from typed_binance import Binance

async with Binance.new() as client:
  account = await client.spot.http.account.info()
  for balance in account['balances']:
    if float(balance['free']) > 0:
      print(balance)
```

USD-M futures has its own balance surface, per asset rather than per-symbol:

```python
from typed_binance import Binance

async with Binance.new() as client:
  balances = await client.usdm_futures.http.account.balance_v3()
```

## Positions

Spot has no positions — only futures and options do. USD-M futures:

```python
from typed_binance import Binance

async with Binance.new() as client:
  positions = await client.usdm_futures.http.trading.position_risk_v3(symbol='BTCUSDT')
  for position in positions:
    print(position['symbol'], position['positionAmt'])
```

Omitting `symbol` returns every symbol with an open position or open order. COIN-M futures
and options expose the equivalent under `client.coinm_futures.http.trading` and
`client.options.http.trading`.

## Trade History

```python
from typed_binance import Binance

async with Binance.new() as client:
  trades = await client.spot.http.account.my_trades(symbol='BTCUSDT', limit=50)
```

`client.spot.http.account` also has `all_orders`, `commission`, `my_prevented_matches`, and more.
USD-M futures, COIN-M futures, options, and portfolio margin each expose their own account
surface the same way, e.g. `client.usdm_futures.http.account`.
