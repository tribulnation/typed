# Fetch Your Balances & Positions

Use `client.info` for account-state reads. These methods take a user address, not a signing wallet.

## Fetch Spot Balances

```python
from hyperliquid import Hyperliquid

user = '0xYourAccountAddress'

async with Hyperliquid.http(public=True) as client:
  spot = await client.info.spot_clearinghouse_state(user=user)
  for balance in spot['balances']:
    print(balance['coin'], balance['total'])
```

## Fetch Perp Balances And Positions

`clearinghouse_state()` returns margin summaries plus open perpetual positions.

If you trade on a non-default perp dex, pass `dex=...`.

```python
from hyperliquid import Hyperliquid

user = '0xYourAccountAddress'

async with Hyperliquid.http(public=True) as client:
  state = await client.info.clearinghouse_state(user=user)
  print(state['marginSummary']['accountValue'])

  for asset_position in state['assetPositions']:
    position = asset_position['position']
    print(position['coin'], position['szi'], position['entryPx'])
```

## Fetch Portfolio History

Use `user_portfolio()` for account-value and PnL history across the built-in periods.

```python
from hyperliquid import Hyperliquid

user = '0xYourAccountAddress'

async with Hyperliquid.http(public=True) as client:
  portfolio = await client.info.user_portfolio(user=user)
  print(portfolio)
```

## Fetch Subaccounts

`sub_accounts()` returns both perp and spot state for each of the account's subaccounts,
or `None` when it has none.

```python
from hyperliquid import Hyperliquid

user = '0xYourAccountAddress'

async with Hyperliquid.http(public=True) as client:
  sub_accounts = await client.info.sub_accounts(user=user)
  print([account['name'] for account in sub_accounts or []])
```
