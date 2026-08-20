# Manage Deposits & Withdrawals

These calls are signed — see [API Keys Setup](../api-keys.md).

## Deposit Address

```python
from typed_binance import Binance

async with Binance.new() as client:
  deposit = await client.spot.http.wallet.capital.deposit.address(coin='USDT', network='TRX')
  print(deposit['address'], deposit['tag'])
```

Omitting `network` uses the coin's default network. `client.spot.http.wallet.capital.config.get_all()`
lists every coin's supported networks, including which one is the default.

## Deposit History

```python
from typed_binance import Binance

async with Binance.new() as client:
  deposits = await client.spot.http.wallet.capital.deposit.history(coin='USDT')
  for deposit in deposits:
    print(deposit['coin'], deposit['status'])
```

## Withdraw

```python
from typed_binance import Binance

async with Binance.new() as client:
  withdrawal = await client.spot.http.wallet.capital.withdraw.apply(
    coin='USDT', network='TRX', address='...', amount=10,
  )
  print(withdrawal['id'])
```

`address_tag` is required when the destination network needs a memo/tag (check
`capital.config.get_all()`'s `networkList[].withdrawTag`). `client.spot.http.wallet.capital.withdraw.quota()`
returns the account's remaining 24-hour withdrawal quota.

## Withdraw History

```python
from typed_binance import Binance

async with Binance.new() as client:
  withdrawals = await client.spot.http.wallet.capital.withdraw.history(coin='USDT')
  for withdrawal in withdrawals:
    print(withdrawal['id'], withdrawal['status'])
```
