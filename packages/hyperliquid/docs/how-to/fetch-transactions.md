# Fetch Your Transactions

Use `client.info` for account history reads. These methods take a user address and Python `datetime` bounds where applicable. Use timezone-aware values; the client converts them to wire milliseconds automatically. See [Timestamps](../reference/timestamps.md).

## Fetch Trades

Use `user_fills()` for recent fills or `user_fills_by_time()` for a specific window.

```python
from datetime import datetime, timedelta, timezone
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

async with Hyperliquid.new(public=True) as client:
  fills = await client.info.user_fills_by_time(user=user, start_time=start_time, end_time=end_time)
  for fill in fills:
    print(fill['coin'], fill['side'], fill['px'], fill['sz'])
```

For large windows, use `user_fills_by_time_paged()`. Hyperliquid returns at most 2000
fills per response, oldest first; the pager moves `start_time` forward to the latest fill
time of each full page, re-reads that millisecond and drops the fills it already returned,
and stops on the first page shorter than 2000. `await` it for every fill in one list:

```python
from datetime import datetime, timedelta, timezone
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=90)

async with Hyperliquid.new(public=True) as client:
  fills = await client.info.user_fills_by_time_paged(user=user, start_time=start_time, end_time=end_time)
  print(len(fills))
```

## Fetch Funding Payments

```python
from datetime import datetime, timedelta, timezone
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

async with Hyperliquid.new(public=True) as client:
  funding = await client.info.user_funding(user=user, start_time=start_time, end_time=end_time)
  for entry in funding:
    delta = entry['delta']
    print(delta['coin'], delta['usdc'], delta['fundingRate'])
```

For long ranges, use `user_funding_paged()`. It moves `start_time` forward to the latest
`time` of each full page and stops on the first shorter one; `await` it for every entry
flattened, or `async for` it to handle one page at a time.

```python
from datetime import datetime, timedelta, timezone
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

async with Hyperliquid.new(public=True) as client:
  async for chunk in client.info.user_funding_paged(user=user, start_time=start_time, end_time=end_time):
    print(len(chunk))
```

## Fetch Other Ledger Flows

Use `user_non_funding_ledger_updates()` for non-funding transfers and ledger events:
deposits, withdrawals, spot and sub-account transfers, vault flows, staking, liquidations,
and rewards.

```python
from datetime import datetime, timedelta, timezone
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

async with Hyperliquid.new(public=True) as client:
  flows = await client.info.user_non_funding_ledger_updates(
    user=user,
    start_time=start_time,
    end_time=end_time,
  )
  for entry in flows:
    print(entry['time'], entry['delta']['type'])
```

Each `delta` is a union discriminated on `type`, so checking `type` narrows the entry to
the exact variant and its fields:

```python
from datetime import datetime, timedelta, timezone
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

async with Hyperliquid.new(public=True) as client:
  flows = await client.info.user_non_funding_ledger_updates(
    user=user, start_time=start_time, end_time=end_time,
  )
  for entry in flows:
    delta = entry['delta']
    if delta['type'] == 'deposit':
      print('deposited', delta['usdc'])
    elif delta['type'] == 'withdraw':
      print('withdrew', delta['usdc'], 'fee', delta['fee'])
    elif delta['type'] == 'send':
      print('sent', delta['amount'], delta['token'], 'to', delta['destination'])
    elif delta['type'] == 'vaultWithdraw':
      print('vault withdrawal', delta['netWithdrawnUsd'], 'from', delta['vault'])
```

With response validation enabled, monetary amounts are parsed into `decimal.Decimal`.
Keep them as decimals when doing arithmetic to preserve precision.

Hyperliquid adds ledger types over time, and an unrecognized `type` raises a
`ValidationError` rather than validating as an opaque value. This is deliberate: ledger
deltas move balances, so a silently-ignored new type would corrupt any accounting built on
this endpoint. Failing loudly surfaces the new type so it can be modeled.

To tolerate unmodeled types, validate each delta individually and handle the failures
explicitly, rather than letting one unknown row abort a whole history read:

```python
from datetime import datetime, timezone
from typed_hyperliquid.info import Info
from typed_hyperliquid.info.user_non_funding_ledger_updates import UserNonFundingLedgerEntry
import pydantic

entry_adapter = pydantic.TypeAdapter(UserNonFundingLedgerEntry)

address = '0xYourAccountAddress'
start_time = datetime.fromtimestamp(0, tz=timezone.utc)

info = Info.http(validate=False)
for raw in await info.user_non_funding_ledger_updates(user=address, start_time=start_time):
  try:
    entry_adapter.validate_python(raw)
  except pydantic.ValidationError:
    print('unrecognized ledger entry', raw)  # log it, or surface it as an unclassified record
    continue
```

## Pagination

The ledger endpoint returns at most **500 entries** per response. Use the generated
pager to fetch a larger range. It re-fetches the boundary timestamp and removes only
previously returned occurrences, preserving other events at that same timestamp.

```python
from datetime import datetime
from typed_hyperliquid.info import Info

async def all_ledger_updates(info: Info, address: str, start_time: datetime):
  async for page in info.user_non_funding_ledger_updates_paged(
    user=address, start_time=start_time,
  ):
    yield page
```

You can also `await info.user_non_funding_ledger_updates_paged(...)` to collect the
entries in one list. Both forms accept an inclusive `end_time` bound.

`hash` is **not** unique: one transaction can emit several deltas, so `(time, hash)`
is not a primary key. The pager preserves duplicate occurrences. If a full page shares
one timestamp and the remaining events cannot be reached, it raises `LogicError`.
