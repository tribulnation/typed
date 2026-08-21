# Manage Deposits & Withdrawals

`wallet` reads and writes need credentials — see [API Keys Setup](../api-keys.md).

## Deposit Address

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  address = await client.http.wallet.address_book.get_current_deposit_address(
    currency='BTC',
  )
  print(address)
```

`create_deposit_address` requests a new one instead of reusing the current one.

## Deposit History

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  deposits = await client.http.wallet.deposits.get_deposits(currency='BTC', count=10)
  for deposit in deposits['data']:
    print(deposit['transaction_id'], deposit['amount'], deposit['state'])
```

## Withdraw

The destination address must already be in this account's address book.

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  withdrawal = await client.http.wallet.withdrawals.withdraw(
    currency='BTC', address='some-address-book-address', amount=0.001,
  )
  print(withdrawal['state'], withdrawal.get('fee'))
```

## Withdrawal History

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  withdrawals = await client.http.wallet.withdrawals.get_withdrawals(
    currency='BTC', count=10,
  )
  for withdrawal in withdrawals['data']:
    print(withdrawal['amount'], withdrawal['state'])
```

`get_deposits` and `get_withdrawals` both have a `_paged` sibling — see
[Paginate Through Results](paginate-through-results.md).
