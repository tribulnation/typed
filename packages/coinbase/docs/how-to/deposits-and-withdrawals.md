# Deposits & Withdrawals

Moving funds in and out of a Coinbase App wallet (`accounts`, v2) is split by rail: fiat through a linked payment method, crypto through a blockchain address. Both need credentials — see [API Keys Setup](../api-keys.md).

## Fiat

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  methods = await client.app.advanced_trade.http.payment_methods.list()
  payment_method = methods['payment_methods'][0]['id']

  deposit = await client.app.accounts.deposits.create(
    'account-id', amount='10.00', currency='USD', payment_method=payment_method,
  )
  await client.app.accounts.deposits.commit('account-id', deposit['transfer']['id'])
  await client.app.accounts.deposits.list('account-id', limit=25)

  withdrawal = await client.app.accounts.withdrawals.create(
    'account-id', amount='10.00', currency='USD', payment_method=payment_method,
  )
  await client.app.accounts.withdrawals.list('account-id', limit=25)
```

`commit=False` on `deposits.create`/`withdrawals.create` stages the transfer without executing it, completed later with `deposits.commit`/`withdrawals.commit`.

## Crypto

Receive by minting a new address; send with a caller-chosen idempotency token so a retried request can't double-send:

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  address = await client.app.accounts.addresses.create('account-id', network='ethereum')
  await client.app.accounts.addresses.list('account-id', limit=25)

  send = await client.app.accounts.transactions.create('account-id', {
    'type': 'send',
    'to': '0x0000000000000000000000000000000000dEaD',
    'amount': '0.001',
    'currency': 'ETH',
    'idem': 'a-unique-uuid-per-send',
  })
```
