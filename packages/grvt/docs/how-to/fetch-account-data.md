# Fetch Account Data

Account reads need an API key (see [API Keys Setup](../api-keys.md)); no signer key is
required. Sub-account reads (`account_summary`, `spot_account_summary`, `positions`, and the
fill, order, position, funding and interest payment histories) default to the configured
trading sub-account; pass `sub_account_id` to read another one. `funding_account_summary`,
`aggregated_account_summary` and `sub_accounts` read the main account and take no
`sub_account_id`.

## Account Summary And Balances

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  summary = await client.trading.account_summary()
  print(summary['total_equity'], summary['available_balance'])
  for balance in summary['spot_balances']:
    print(balance['currency'], balance['balance'])

  funding = await client.trading.funding_account_summary()
  print(funding['result']['main_account_id'], funding['result']['total_equity'])

  print(await client.trading.sub_accounts())
```

`aggregated_account_summary()` totals the main account and every sub-account, and
`spot_account_summary()` covers the spot wallet.

## Positions

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  positions = await client.trading.positions(kind=['PERPETUAL'])
  for position in positions:
    print(
      position['instrument'],
      position['size'],
      position['entry_price'],
      position['unrealized_pnl'],
    )
```

## Fills, Orders And Funding History

```python
from datetime import datetime, timedelta, timezone
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  since = datetime.now(timezone.utc) - timedelta(days=7)

  fills = await client.trading.fill_history(start_time=since, limit=100)
  for fill in fills['result']:
    print(
      fill['event_time'], fill['instrument'], fill['price'], fill['size'], fill['fee']
    )

  orders = await client.trading.order_history(start_time=since)
  funding = await client.trading.funding_payment_history(start_time=since)
  closed = await client.trading.position_history(start_time=since)
  print(len(orders['result']), len(funding['result']), len(closed['result']))
```

Each of these returns one page, newest first, with `limit` capped at 1000. To read a whole
range, use the `_paged` variants (see [Paginate Through Results](paginate-through-results.md)).
`interest_payment_history` and `builder_fill_history` work the same way.
