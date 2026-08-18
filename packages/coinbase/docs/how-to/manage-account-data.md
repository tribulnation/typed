# Manage Account Data

Coinbase exposes account balances two ways — legacy Coinbase App wallets (`accounts`, v2) and Advanced Trade brokerage accounts (`advanced_trade.accounts`, v3). Both need credentials — see [API Keys Setup](../api-keys.md).

## Coinbase App Wallets (v2)

```python
from coinbase import Coinbase

async with Coinbase.new() as client:
  wallets = await client.accounts.list(limit=25)                 # every linked wallet
  wallet_id = wallets['data'][0]['id']
  wallet = await client.accounts.get(wallet_id)                  # one wallet, by id or currency code (e.g. 'BTC')
  history = await client.accounts.transactions.list(wallet_id, limit=25)  # transaction history
```

## Advanced Trade Brokerage Accounts (v3)

```python
from coinbase import Coinbase

async with Coinbase.new() as client:
  accounts = await client.advanced_trade.accounts.list(limit=50)     # every brokerage account
  account_uuid = accounts['accounts'][0]['uuid']
  account = await client.advanced_trade.accounts.get(account_uuid)   # one account by uuid
```

`accounts.list` (v2), `accounts.transactions.list` (v2), and `advanced_trade.accounts.list` (v3) all page — see [Paginate Through Results](paginate-through-results.md).
