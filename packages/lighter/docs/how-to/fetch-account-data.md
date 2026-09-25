# Fetch Account Data

Account data lives under `client.api.account`. Balances and positions are public on
Lighter, so `account.get` works with `public=True`; orders, trades and transfer history need
an auth token, which the client derives from your API key or takes from a read-only token
([Authenticated Setup](../authenticated-setup.md)).

## Balances And Positions

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  found = await client.api.account.get({'by': 'index', 'value': client.signer.account_index})
  account = found['accounts'][0]
  print(account['collateral'], account['available_balance'], account['total_asset_value'])

  for position in account['positions']:
    print(position['symbol'], position['position'], position['avg_entry_price'], position['unrealized_pnl'])

  for asset in account['assets']:  # spot balances
    print(asset['symbol'], asset['balance'], asset['locked_balance'])
```

Look up by wallet instead with `{'by': 'l1_address', 'value': '0x...'}`: that returns the
master account and every sub-account.

## Open Orders

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  account = client.signer.account_index
  active = await client.api.account.orders.active(account_index=account, market_id=0)
  for order in active['orders']:
    print(order['order_index'], order['client_order_index'], order['type'], order['price'], order['status'])

  mine = await client.api.account.orders.by_client_index([1001, 1002], account_index=account)
```

## Order And Trade History

Both are cursor-paged; the `_paged` variants follow the cursor for you
([Paginate Through Results](paginate-through-results.md)).

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  account = client.signer.account_index
  closed = await client.api.account.orders.inactive(account_index=account, limit=50)
  for order in closed['orders']:
    print(order['order_index'], order['status'], order['filled_base_amount'])

  trades = await client.api.account.orders.trades('timestamp', limit=50, account_index=account)
  for trade in trades['trades']:
    print(trade['timestamp'], trade['market_id'], trade['price'], trade['size'])
```

## PnL, Funding And Liquidations

```python
from datetime import datetime, timedelta, timezone

from typed_lighter import Lighter

async with Lighter.new() as client:
  account = client.signer.account_index
  end = datetime.now(timezone.utc)
  pnl = await client.api.account.pnl(
    value=account, resolution='1d', start_timestamp=end - timedelta(days=30), end_timestamp=end, count_back=30
  )
  funding = await client.api.account.position_funding(account_index=account, limit=100)
  liquidations = await client.api.account.liquidations(account_index=account, limit=100)
  limits = await client.api.account.limits(account)  # tier and order-count limits
```

## API Keys And Nonces

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  keys = await client.api.account.keys.list(account_index=476)
  for key in keys['api_keys']:
    print(key['api_key_index'], key['public_key'], key['nonce'])
  nonce = await client.api.account.keys.next_nonce(account_index=476, api_key_index=4)
```

Transfer, deposit and withdrawal history is covered in
[Transfers & Sub-Accounts](transfers-and-sub-accounts.md).
