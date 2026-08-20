# Manage Deposits And Withdrawals

Everything here needs credentials — see [API Keys Setup](../api-keys.md).

## Get Your Deposit Address

`asset.deposit.master_address` returns the master account's deposit address for a coin, one
entry per supported chain:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  addresses = await client.http.asset.deposit.master_address(coin='USDT')
  for chain in addresses['chains']:
    print(chain['chainType'], chain['addressDeposit'], chain['tagDeposit'])
```

Pass `chain_type` (the `chain` value from `asset.coin_info`) to filter to one chain instead of
getting every chain back. `tagDeposit` is an empty string on a chain that doesn't use a memo.

## List Deposit Records

`asset.deposit.record` returns the last 30 days by default:

```python
from datetime import datetime, timedelta, timezone
from typed_bybit import Bybit

async with Bybit.new() as client:
  page = await client.http.asset.deposit.record(
    coin='USDT',
    start_time=datetime.now(timezone.utc) - timedelta(days=7),
    end_time=datetime.now(timezone.utc),
    limit=50,
  )
  for deposit in page['rows']:
    print(deposit['coin'], deposit['amount'], deposit['status'])
```

`start_time`/`end_time` take a real `datetime`, not a millisecond integer. `record` returns at
most `limit` rows per call; walk the full history with `record_paged` instead — see
[Paginate Through Results](paginate-through-results.md).

## Submit A Withdrawal

`asset.withdraw.create` takes one request dict and moves real funds — start with a small
amount until you've confirmed the address and chain are right:

```python
from datetime import datetime, timezone
from typed_bybit import Bybit

async with Bybit.new() as client:
  result = await client.http.asset.withdraw.create({
    'coin': 'USDT',
    'chain': 'TRX',
    'address': 'T...',
    'amount': '10',
    'timestamp': datetime.now(timezone.utc),
    'accountType': 'FUND',
  })
  print(result['id'])
```

`timestamp` is the current time as a `datetime`; `accountType` is one of `'FUND'`, `'UTA'`, or
`'EARN'` and selects which wallet the withdrawal draws from. `tag` is required when the
destination address uses one, and `forceChain` overrides Bybit's own chain-routing detection
when you need to force on-chain, off-chain, or a UID transfer explicitly.

## List Withdrawal Records

`asset.withdraw.record` mirrors `deposit.record`, and also returns the last 30 days by default:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  page = await client.http.asset.withdraw.record(coin='USDT', limit=50)
  for withdrawal in page['rows']:
    print(withdrawal['withdrawId'], withdrawal['status'], withdrawal['amount'])
```

Filter by `withdraw_id`, `tx_id`, or `withdraw_type` (`0` on-chain, `1` off-chain, `2` UID
transfer) instead of scanning every row. Like `deposit.record`, a single call returns at most
`limit` rows — `withdraw.record_paged` walks the full history the same way.
