# Fetch Account Data

These calls are private -- see [API Keys Setup](../api-keys.md) first.

## Balances

```python
from kraken import Kraken

async with Kraken.new() as client:
  balances = await client.spot.account.balance()
  print(balances)  # {'ZUSD': '10.0000', 'USDC': '9.9500', ...}
```

`balance_ex()` returns the same per-asset balances with `balance`/`hold_trade` split out;
`trade_balance()` returns a margin/equity summary instead of raw per-asset balances.

## Positions

```python
from kraken import Kraken

async with Kraken.new() as client:
  positions = await client.spot.account.open_positions()
```

Only relevant for margin positions -- empty for an account with no open leveraged
positions.

## Trade & Ledger History

```python
from kraken import Kraken

async with Kraken.new() as client:
  trades = await client.spot.account.trades_history()
  ledgers = await client.spot.account.ledgers()
  one_trade = await client.spot.account.query_trades(txid='TXID123-ABCDE-XXXXXX')
  one_ledger = await client.spot.account.query_ledgers(id='LEDGER123-ABCDE')
```

`trades_history`/`ledgers` return recent entries, most recent first -- page further back
with `ofs`/`start`/`end`. `query_trades`/`query_ledgers` look up specific ids instead.
