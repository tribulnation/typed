# Manage Account Data

These calls need credentials — see [API Keys Setup](../api-keys.md).

## Balances

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  accounts = await client.account.spot_accounts(currency='USDT')
  for account in accounts:
    print(account['type'], account['currency'], account['available'])
```

Deposits land in the `main` account first; use `account.transfer` to move funds into
`trade` before they can be used to place orders.

## Ledger History

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  page = await client.account.ledgers(currency='USDT', page_size=50)
  for entry in page['items']:
    print(entry['bizType'], entry['amount'], entry['balance'])
```

`account.ledgers` covers Spot/Margin; `account.hf_ledgers` covers the high-frequency
trading account; `account.futures_ledgers` covers Futures. See
[Paginate Through Results](paginate-through-results.md) for walking a full history.

## Futures Positions

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  positions = await client.futures.positions.get_position_list(currency='USDT')
  for position in positions:
    print(position['symbol'], position['currentQty'])
```

## Account Info

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  info = await client.account.user_info()
  print(info)
```
