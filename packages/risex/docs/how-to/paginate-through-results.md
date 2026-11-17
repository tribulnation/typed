# Paginate Through Results

Paginated history endpoints return one page per call. Each of them has a `_paged` twin that walks every page for you:

| Single page | Walks every page |
| --- | --- |
| `client.markets.trade_history` | `client.markets.trade_history_paged` |
| `client.markets.funding_rate_history` | `client.markets.funding_rate_history_paged` |
| `client.account.trade_history` | `client.account.trade_history_paged` |
| `client.account.funding_payments` | `client.account.funding_payments_paged` |
| `client.account.transfer_history` | `client.account.transfer_history_paged` |
| `client.account.positions` | `client.account.positions_paged` |
| `client.orders.history` | `client.orders.history_paged` |
| `client.orders.tpsl.query` | `client.orders.tpsl.query_paged` |
| `client.portfolio.realized_pnl` | `client.portfolio.realized_pnl_paged` |
| `client.competitions.all`, `client.competitions.leaderboard`, `client.affiliate.referrals` | their `_paged` twins |

`client.affiliate.referrals` reads your own referrals, so it needs a client with keys (it logs in for a JWT); every other endpoint above works on a `public=True` client.

## One Page At A Time

```python
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'

async with RISEx.new(public=True) as client:
  first = await client.account.trade_history(ACCOUNT, page=1, limit=100)
  print(len(first['trades']), first['has_next_page'])
```

Most histories take a 1-based `page` and a `limit` of up to 1000 (default 100); positions take a `page_size` instead. Competitions and competition leaderboards take an `offset` and a `limit` of up to 500.

Two list endpoints have no `_paged` twin. `client.orders.open` has been observed to return every resting order in one reply, with no effect from `limit` or `start_index`, and `client.points.history` takes no page parameters and returns every epoch at once.

## Every Row

Awaiting a `_paged` method returns every row of every page as one list:

```python
from datetime import datetime, timedelta, timezone
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'

async with RISEx.new(public=True) as client:
  now = datetime.now(timezone.utc)
  trades = await client.account.trade_history_paged(
    ACCOUNT, start_time=now - timedelta(days=30), end_time=now, limit=500
  )
  print(len(trades))
```

Pass a fixed `end_time`. Histories are newest first, so on an active account a trade made during the walk lands on page 1 and pushes every later page back by one row: without an upper bound the walk returns that row twice. A fixed `end_time` excludes anything newer and keeps every page where it was.

## Page By Page

Iterating yields one page (a list of rows) at a time, so you can stop early:

```python
from datetime import datetime, timezone
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'

async with RISEx.new(public=True) as client:
  now = datetime.now(timezone.utc)
  async for page in client.orders.history_paged(account=ACCOUNT, end_time=now, limit=100):
    for order in page:
      print(order['id'], order['side'], order['price'], order['size'])
```

The walk stops at the first short or empty page, or once it has covered the total the response reports. Histories are sorted newest first by default; pass `sorted_by='time'` (or `'created_at'` for orders) for oldest first.
