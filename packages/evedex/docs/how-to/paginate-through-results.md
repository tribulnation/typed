# Paginate Through Results

Paginated endpoints have two methods: the plain one returns a single page, and a `_paged`
variant walks every page for you.

| `_paged` method | Rows |
| --- | --- |
| `client.exchange.orders.list_paged` | Order history |
| `client.exchange.fills_paged` | Fills in a time range |
| `client.exchange.positions.history_paged` | Closed positions |
| `client.exchange.tpsl.list_paged` | Take-profit/stop-loss orders |
| `client.exchange.transfers.list_paged` | Transfers |
| `client.exchange.account.funding_transfers_paged` | Trading-balance ledger |
| `client.exchange.sub_accounts.orders_paged` / `position_history_paged` | A sub-account's orders and closed positions |
| `client.auth.api_keys.list_paged` | API keys |
| `client.auth.user.wallet_transfers_paged` | Wallet transfers |
| `client.market_data.candles_paged` | Candle history |

## One Page at a Time

Account lists take `limit` and `offset` and return `{list, count}`, where `count` is the
total number of matching rows.

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  page = await client.exchange.orders.list(instrument='BTCUSD', limit=100, offset=0)
  print(len(page['list']), 'of', page['count'])
```

## Every Page

A `_paged` call is awaitable, returning every row in one list, or async-iterable, yielding
one page of rows at a time. It advances `offset` until it has covered `count` rows.

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  orders = await client.exchange.orders.list_paged(instrument='BTCUSD', status='FILLED')
  print(len(orders))

  async for rows in client.exchange.positions.history_paged(limit=100):
    for position in rows:
      print(position)
```

## Candle History

A single candle request returns at most `limit` rows, keeping the newest ones in the range.
`candles_paged` walks backwards from `before` until it reaches `after`, so pages arrive
newest first; awaiting it returns every candle in the range.

```python
from datetime import datetime, timedelta, timezone
from typed_evedex import Evedex

now = datetime.now(timezone.utc)
async with Evedex.new(public=True) as client:
  candles = await client.market_data.candles_paged(
    instrument='BTCUSD', group='1m', after=now - timedelta(days=1), before=now, limit=500
  )
  print(len(candles))  # 1440 one-minute candles
```

## Retry and Resume

Each page is one independent, read-only request, so a failed page can be retried and a walk
can be resumed from any page:

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  walk = client.exchange.transfers.list_paged(limit=50)
  async for page in walk.pages():
    print(len(page.rows), page.next)  # save page.next to resume later with walk.resume(...)
```
