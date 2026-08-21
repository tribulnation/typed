# Deposits & Withdrawals

`client.account.deposit` and `client.account.withdrawals` cover moving funds on and off
KuCoin. These calls need credentials — see [API Keys Setup](../api-keys.md).

## Get A Deposit Address

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  addresses = await client.account.deposit.address(currency='USDT', chain='trx')
  for address in addresses:
    print(address['address'], address['chainId'])
```

`account.deposit.add` provisions a new address for a currency that doesn't have one yet.

## Deposit History

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  page = await client.account.deposit.history(currency='USDT', status='SUCCESS')
  for entry in page['items']:
    print(entry['currency'], entry['amount'], entry['status'])
```

`account.deposit.history_paged` walks every page automatically — see
[Paginate Through Results](paginate-through-results.md).

## Withdrawal Quota

Check the current limit, fee, and minimum size before submitting a withdrawal:

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  quota = await client.account.withdrawals.quotas(currency='USDT', chain='trx')
  print(quota['availableAmount'], quota['withdrawMinFee'])
```

## Submit A Withdrawal

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  result = await client.account.withdrawals.withdraw({
    'currency': 'USDT',
    'toAddress': 'destination-address',
    'amount': '10',
    'withdrawType': 'ADDRESS',
    'chain': 'trx',
  })
  print(result['withdrawalId'])
```

## Withdrawal History & Cancellation

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  page = await client.account.withdrawals.history(currency='USDT')
  for entry in page['items']:
    print(entry['id'], entry['status'])

  await client.account.withdrawals.cancel('withdrawal-id')
```

A withdrawal can only be cancelled while it's still in `PROCESSING`/`REVIEW` status.
