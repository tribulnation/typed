# Paginate Through Results

GRVT returns history newest first, at most `limit` rows per call (500 by default, 1000 at
most), and the edge's referral data in numbered pages of `page_size` rows. A single call
silently stops at its page, so use the `_paged` variant of a method to read a whole range.
It takes the same arguments minus the cursor (or `page_number`).

| Method | Rows |
| --- | --- |
| `market.trade_history_paged` | public trades |
| `market.funding_rate_paged` | funding rates |
| `market.candlesticks_paged` | candles |
| `trading.fill_history_paged` | your fills |
| `trading.order_history_paged` | your past orders |
| `trading.position_history_paged` | your position lifecycles, closed or partially closed |
| `trading.funding_payment_history_paged`, `trading.interest_payment_history_paged` | funding and interest payments |
| `trading.transfer_history_paged`, `trading.deposit_history_paged`, `trading.withdrawal_history_paged` | funding movements |
| `trading.builder_fill_history_paged` | fills you earned builder fees on |
| `edge.referral_data_paged`, `edge.indirect_referral_data_paged` | referral data |

`vault_manager_investor_history` takes no cursor and has no `_paged` variant.

## Read Everything

Awaiting a `_paged` call fetches every page and returns one list:

```python
from datetime import datetime, timedelta, timezone
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  since = datetime.now(timezone.utc) - timedelta(days=30)
  fills = await client.trading.fill_history_paged(start_time=since, limit=1000)
  print(len(fills), sum(fill['fee'] for fill in fills))
```

## One Page At A Time

Iterating yields one page (a list of rows) per request, so you can stop early:

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  pages = client.market.trade_history_paged(instrument='BTC_USDT_Perp', limit=100)
  async for page in pages:
    for trade in page:
      print(trade['event_time'], trade['price'])
    break
```

## Candles

`candlesticks_paged` walks back from `end_time` (now, when unset) to `start_time`:

```python
from datetime import datetime, timedelta, timezone
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  candles = await client.market.candlesticks_paged(
    'BTC_USDT_Perp',
    interval='CI_1_H',
    type='TRADE',
    start_time=datetime.now(timezone.utc) - timedelta(days=30),
    limit=1000,
  )
  print(len(candles), candles[-1]['open_time'])
```

## Resume Or Retry

Each page is fetched from a saved state, so a walk can be checkpointed and resumed later:

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  walk = client.market.funding_rate_paged(instrument='BTC_USDT_Perp')
  checkpoint = None
  async for page in walk.pages():
    print(len(page.rows))
    checkpoint = page.next  # None after the last page
    break

  if checkpoint is not None:
    async for rows in walk.resume(checkpoint):
      print(len(rows))  # continues where the first walk stopped
      break
```

`walk.via(call)` routes every page fetch through your own wrapper, for example a retry
policy.
