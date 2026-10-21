# Fetch Account Data

Most account reads take the account address and are unsigned, so a public client can read
any account. The `user` reads about the signer's own account sign instead and need a wallet:
`get_user`, `get_following_list` and `get_deposit_address`, as does the master-only
`exchange.get_agents`. Amounts come back as `Decimal`, timestamps as `datetime`.

## Balances And Positions

`info.clearinghouse_state` is the perpetuals account: margin summary, withdrawable USDC and
every open position. `info.spot_clearinghouse_state` holds the spot wallet.

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  state = await client.info.clearinghouse_state(user=address)
  print(state['marginSummary']['accountValue'], state['withdrawable'])
  for item in state['assetPositions']:
    position = item['position']
    print(position['coin'], position['szi'], position['entryPx'], position['unrealizedPnl'])

  spot = await client.info.spot_clearinghouse_state(address)
  for balance in spot['balances']:
    print(balance['coin'], balance['total'])
```

`szi` is signed: positive is long, negative short.

## Fills And Funding

```python
from datetime import datetime, timedelta, timezone
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  fills = await client.info.user_fills(address)
  for fill in fills:
    print(fill['time'], fill['coin'], fill['side'], fill['px'], fill['sz'], fill['closedPnl'])

  week_ago = datetime.now(timezone.utc) - timedelta(days=7)
  recent = await client.info.user_fills_by_time(address, start_time=week_ago)
  funding = await client.info.user_funding(address, start_time=week_ago)
```

For a range longer than one response, use `user_fills_by_time_paged` (see
[Paginate Through Results](paginate-through-results.md)).

## Orders, Fees And Transfers

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  history = await client.info.historical_orders(address)  # recent orders, with status
  fees = await client.info.user_fees(address)  # fee rates and volume
  transfers = await client.user.get_transfer_history(address)
  for item in transfers['items']:
    print(item['type'], item['status'], item['asset'], item['amountChange'])
```

## Performance

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  performance = await client.user.get_performance(address=address, time_range='1W')
  pnl = await client.user.get_pnl_history(address=address, time_range='1M')
  today = await client.user.get_today_data(address)
  volume = await client.user.get_user_trade_vol(address)
```

## Your Profile

```python
import os
from typed_margin_trade import MarginTrade

async with MarginTrade.new(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'], mainnet=False) as client:
  profile = await client.user.get_user()
  print(profile['userAddress'], profile['status'], profile.get('faucetClaimableToday'))
  starred = await client.user.get_following_list()  # markets you follow
```

Signed as an agent, `get_user` returns the master account's profile.

## Referrals

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  referrals = await client.user.get_referral_details(address)
  code = await client.user.get_my_invite_code(address)
```
