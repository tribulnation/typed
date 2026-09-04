# Deposits & Withdrawals

Moving funds in and out of a Coinbase App wallet (`accounts`, v2) is split by rail: fiat through a linked payment method, crypto through a blockchain address. Both need credentials — see [API Keys Setup](../api-keys.md).

## Fiat

```python
from decimal import Decimal

from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  methods = await client.app.advanced_trade.http.payment_methods.list()
  payment_method = methods['payment_methods'][0]['id']

  deposit = await client.app.accounts.deposits.create(
    account_id='account-id', amount=Decimal('10.00'), currency='USD', payment_method=payment_method,
  )
  await client.app.accounts.deposits.commit(
    account_id='account-id', deposit_id=deposit['transfer']['id'],
  )
  await client.app.accounts.deposits.list(account_id='account-id', limit=25)

  withdrawal = await client.app.accounts.withdrawals.create(
    account_id='account-id', amount=Decimal('10.00'), currency='USD', payment_method=payment_method,
  )
  await client.app.accounts.withdrawals.list(account_id='account-id', limit=25)
```

`commit=False` on `deposits.create`/`withdrawals.create` stages the transfer without executing it, completed later with `deposits.commit`/`withdrawals.commit`.

## Crypto

Receive by minting a new address; send with a caller-chosen idempotency token so a retried request can't double-send:

```python
from decimal import Decimal

from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  address = await client.app.accounts.addresses.create(account_id='account-id', network='ethereum')
  await client.app.accounts.addresses.list(account_id='account-id', limit=25)

  send = await client.app.accounts.transactions.create(
    account_id='account-id',
    type='send',
    to='0x0000000000000000000000000000000000dEaD',
    amount=Decimal('0.001'),
    currency='ETH',
    idem='a-unique-uuid-per-send',
  )
```
