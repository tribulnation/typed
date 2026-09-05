# Fetch Account Data

`client.account` and `client.position` report balances, positions, fills, and
ledger activity. They need credentials — see [API Keys Setup](../api-keys.md).

## Wallet Balance

`wallet_balance` requires `account_type` as a keyword argument, one of `'UNIFIED'`,
`'CONTRACT'`, or `'SPOT'`:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  balance = await client.account.wallet_balance(account_type='UNIFIED')
  account = balance['list'][0]
  print(account['totalEquity'])
  for coin in account['coin']:
    print(coin['coin'], coin['equity'], coin['walletBalance'])
```

Pass `coin='USDT,USDC'` to restrict the coins returned; by default every coin with a
non-zero balance or liability comes back.

## Positions

`client.position.list` reports open positions for `'linear'`, `'inverse'`, or
`'option'` — spot has no positions, so `category` never accepts `'spot'` here:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  page = await client.position.list(category='linear', settle_coin='USDT')
  for position in page['list']:
    print(position['symbol'], position['side'], position['size'], position['unrealisedPnl'])
```

Pass `symbol` to look up one symbol regardless of whether a position exists, or
`settle_coin`/`base_coin` to scope a whole category. `position.list` also has a
`list_paged` iterator; see [Paginate Through Results](paginate-through-results.md).

## Trade History

`client.trade.trade_history` returns your executions (fills), not order state —
one order can produce several:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  page = await client.trade.trade_history(category='spot', symbol='BTCUSDT', limit=50)
  for execution in page['list']:
    print(execution['execId'], execution['execPrice'], execution['execQty'])
```

`start_time`/`end_time` bound the query (7 days apart at most; last 7 days if both are
omitted), and `exec_type` filters by execution kind, for example `'Trade'` or `'Funding'`.
It also has a `trade_history_paged` iterator.

## Transaction Log

`client.account.transaction_log` reports ledger-level account activity in a Unified
account — transfers, trades, funding, settlements, and more — going back up to two years:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  page = await client.account.transaction_log(category='linear', limit=50)
  for entry in page['list']:
    print(entry['type'], entry['currency'], entry['change'], entry['cashBalance'])
```

Every argument is optional; narrow with `category`, `currency`, `type`, or `start_time`/
`end_time`. A `transaction_log_paged` iterator is also available.
