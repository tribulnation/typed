# Paginate Through Results

Five calls have a `_paged` variant that walks every page for you:

| Method | Walks |
| - | - |
| `info.user_fills_by_time_paged` | an account's fills over a time range |
| `info.get_liquidations_paged` | every account's liquidations |
| `info.get_liquidation_feed_paged` | the public liquidation event feed, optionally one market |
| `public.announcements.list_paged` | exchange announcements |
| `user.get_referral_details_paged` | accounts an account has referred |

Each returns a `PaginatedResponse`: `await` it for every row at once, or iterate it with
`async for` to handle one page at a time.

The two liquidation walks are long (hundreds of thousands of rows on testnet, over a
million on mainnet), so take a page or two, or bound the feed with `start_time`, rather
than awaiting them whole. `page_size` is at most 1000 on both; a larger size is clamped to
1000 by the venue.

## Every Row At Once

```python
from datetime import datetime, timedelta, timezone
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  start = datetime.now(timezone.utc) - timedelta(days=30)
  fills = await client.info.user_fills_by_time_paged(address, start_time=start)
  print(len(fills), 'fills')
```

`user_fills_by_time` alone returns at most one response's worth of fills; the paged variant
keeps moving `end_time` back until it reaches `start_time`, without duplicating or skipping
fills that share a timestamp.

## One Page At A Time

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  async for page in client.info.get_liquidations_paged(page_size=100):
    for liquidation in page:
      print(liquidation['timestamp'], liquidation['user'])
    break  # stop whenever you have enough

  async for page in client.info.get_liquidation_feed_paged('BTC', page_size=100):
    for event in page:
      print(event['timestamp'], event['kind'], event['liquidatedAddress'])
    break

  async for page in client.public.announcements.list_paged():
    for announcement in page:
      print(announcement['category'], announcement['title'])
```

`get_liquidations_paged` (and `get_liquidations`) take no account: the venue always returns
every account's liquidations. To find one account's, filter on each row's `user` yourself:

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  pages = 0
  async for page in client.info.get_liquidations_paged(page_size=1000):
    mine = [row for row in page if row['user'] == address]
    print(len(mine), 'of', len(page))
    pages += 1
    if pages == 3:
      break
```

## Resuming

`pages()` yields each page with the state it was fetched from and the state of the next one,
so a long walk can be checkpointed and resumed with `resume(state)`:

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  referrals = client.user.get_referral_details_paged(address, limit=50)
  async for page in referrals.pages():
    print(len(page.rows), page.next)
    if page.next is not None:
      rest = await referrals.resume(page.next)
    break
```
