# Manage Account Data

Coinbase exposes account balances two ways — legacy Coinbase App wallets (`app.accounts`, v2) and Advanced Trade brokerage accounts (`app.advanced_trade.http.accounts`, v3). Both need credentials — see [API Keys Setup](../api-keys.md).

## Coinbase App Wallets (v2)

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  wallets = await client.app.accounts.list(limit=25)                 # every linked wallet
  wallet_id = wallets['data'][0]['id']
  wallet = await client.app.accounts.get(wallet_id)                  # one wallet, by id or currency code (e.g. 'BTC')
  history = await client.app.accounts.transactions.list(account_id=wallet_id, limit=25)  # transaction history
```

## Advanced Trade Brokerage Accounts (v3)

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  accounts = await client.app.advanced_trade.http.accounts.list(limit=50)     # every brokerage account
  account_uuid = accounts['accounts'][0]['uuid']
  account = await client.app.advanced_trade.http.accounts.get(account_uuid)   # one account by uuid
```

`app.accounts.list` (v2), `app.accounts.transactions.list` (v2), and `app.advanced_trade.http.accounts.list` (v3) all page — see [Paginate Through Results](paginate-through-results.md).
