# Paginate Through Results

Every paged Lighter endpoint has a `_paged` twin that walks the pages for you. It takes the
same arguments minus the cursor, and returns a `PaginatedResponse` you can await (every row,
flattened) or iterate (one page at a time).

## Cursor-Paged History

Account orders, trades, funding, liquidations, transfers, leases, referrals and RFQs follow
Lighter's cursor:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  account = client.signer.account_index

  trades = await client.api.account.orders.trades_paged('timestamp', limit=100, account_index=account)
  print(len(trades), 'trades')

  async for page in client.api.account.orders.inactive_paged(account_index=account, limit=100):
    for order in page:
      print(order['order_index'], order['status'])
```

`limit` is the page size, not a total. Two rules end a cursor walk:

- orders, trades, funding, liquidations, leases and RFQs stop when Lighter sends no
  further `next_cursor`;
- `transfers.history`, `transfers.deposits`, `transfers.withdrawals` and
  `referral.user_referrals` echo a `cursor` that is not a reliable end marker (withdrawals
  repeats the same cursor on an empty page), so they stop on the first empty page.

## Time Ranges

`fundings_paged` covers a range wider than one response (749 fundings) by moving
`end_timestamp` back to the earliest row of each full page.
Pages therefore arrive **newest first**; rows inside a page stay oldest first.

```python
from datetime import datetime, timedelta, timezone

from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  end = datetime(2026, 9, 1, tzinfo=timezone.utc)
  fundings = await client.api.markets.fundings_paged(
    market_id=0,
    resolution='1h',
    start_timestamp=end - timedelta(days=60),
    end_timestamp=end,
    count_back=0,
  )
  fundings = sorted(fundings, key=lambda funding: funding['timestamp'])
```

Candles and mark-price candles have no paged method: walk them in windows instead
([Fetch Market Data](fetch-market-data.md#candles)).

## Pools And Leaderboards

`pools.list_paged` walks pools in descending account index: start `index` at the top,
`281474976710655`, and it moves below the lowest index of each page.
`points.pnl_leaderboard_paged` advances an offset until it has covered the `total` Lighter
reports:

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  pools = await client.api.pools.list_paged('user', index=281474976710655, limit=100)
  frozen = [pool['account_index'] for pool in pools if pool['status'] == 1]

  async for page in client.api.points.pnl_leaderboard_paged('7d', sort_by='roi', limit=100):
    for entry in page:
      print(entry['rank'], entry['l1_address'], entry['roi'])
    break  # the top 100 is enough
```

## Chain History

The block explorer pages executed transactions by offset:

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  async for page in client.explorer.market_logs_paged('ETH', limit=100):
    for log in page:
      print(log['time'], log['tx_type'], log['hash'])
    break

  history = await client.explorer.account_logs_paged(476, limit=100)
```

`client.api.chain` has index-paged `blocks_paged`, `txs_paged` and `account_txs_paged` too.
Lighter's mainnet host refuses those block and transaction list reads (HTTP 403); they answer
on testnet, and the explorer covers the same history on mainnet.

Stopping early is free: breaking out of `async for` fetches nothing further.

## Resume And Retry

Each page is one independent request, so a walk can be checkpointed and resumed, or each
page fetch wrapped in your own retry. `page.next` is the state the following page is
fetched with (`None` after the last page); keep it only once a page is fully handled, and a
page that fails is fetched again from the saved state with `walk.resume(...)`:

```python
from typed_lighter import Lighter, NetworkError

async with Lighter.new() as client:
  walk = client.api.account.transfers.history_paged(client.signer.account_index)

  checkpoint = walk.init  # the state the next page is fetched with
  failures = 0
  while checkpoint is not None:
    try:
      async for page in walk.resume(checkpoint).pages():
        for row in page.rows:
          print(row['id'], row['type'], row['amount'])
        checkpoint = page.next  # saved only after the page is handled
    except NetworkError:
      failures += 1
      if failures == 3:
        raise
      # the failed page was never checkpointed: the next pass refetches exactly it
```

The checkpoint is plain data (here the venue's cursor string), so it can also be stored
and the walk resumed from it later, in another process.

`walk.via(call)` routes every page fetch through `call`, a function that receives a
zero-argument coroutine function and awaits it, which is where a retry policy goes.
