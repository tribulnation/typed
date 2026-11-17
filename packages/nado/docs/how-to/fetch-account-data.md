# Fetch Account Data

Account reads are public on Nado: anyone can read any subaccount's balances, orders and
history. On a client built with a key, per-subaccount methods default to your own
subaccount; on a `public=True` client, pass the subaccount explicitly.

A subaccount is identified by `bytes32` hex: the owner's 20-byte address followed by the
subaccount name (`default` unless you created others). Build it with `subaccount_bytes32`:

```python
from typed_nado.core import subaccount_bytes32

me = subaccount_bytes32('0xYourWalletAddress', 'default')
```

The examples below use a signing client and its own subaccount; add `me` (as the first
argument, or `subaccount=me`/`subaccounts=[me]`) to read someone else's.

## Balances And Health

```python
from typed_nado import Nado

async with Nado.new() as client:
  info = await client.gateway.subaccount_info()
  for balance in info['spot_balances']:
    print('spot', balance['product_id'], balance['balance']['amount'] / 10**18)
  for position in info['perp_balances']:
    print('perp', position['product_id'], position['balance']['amount'] / 10**18)

  initial, maintenance, unweighted = info['healths']
  print(initial['health'] / 10**18, maintenance['health'] / 10**18)
```

`healths` holds the initial, maintenance and unweighted health; a negative maintenance
health means the subaccount can be liquidated. `isolated_positions()` lists the isolated
margin subaccounts attached to yours.

## Open Orders

```python
from typed_nado import Nado

async with Nado.new() as client:
  btc = await client.gateway.subaccount_orders(product_id=2)
  for order in btc['orders']:
    print(order['digest'], order['price_x18'] / 10**18, order['unfilled_amount'] / 10**18)

  several = await client.gateway.orders(product_ids=[2, 4])
  for product in several['product_orders']:
    print(product['product_id'], len(product['orders']))
```

## Fees And Order Sizing

```python
from typed_nado import Nado

async with Nado.new() as client:
  fees = await client.gateway.fee_rates()
  print(fees['fee_tier'], fees['taker_fee_rates_x18'][2] / 10**18)

  size = await client.gateway.max_order_size(
    product_id=2, price_x18=60_000 * 10**18, direction='long'
  )
  print(size['max_order_size'] / 10**18)
```

## Fills, Orders And Events

The archive (indexer) holds the full history. Its subaccount filters are lists:

```python
from typed_nado import Nado
from typed_nado.core import subaccount_bytes32

me = subaccount_bytes32('0xYourWalletAddress', 'default')

async with Nado.new(public=True) as client:
  matches = await client.archive.matches([me], product_ids=[2], limit=50)
  for match in matches['matches']:
    print(match['digest'], match['base_filled'] / 10**18, match['fee'] / 10**18)

  orders = await client.archive.orders(subaccounts=[me], limit=50)
  events = await client.archive.events([me], event_types=['deposit_collateral', 'withdraw_collateral'])
```

## Positions, Funding And Portfolio

```python
from typed_nado import Nado

async with Nado.new() as client:
  positions = await client.archive.positions(open=True)
  payments = await client.archive.interest_and_funding(product_ids=[2], limit=100)
  for payment in payments['funding_payments']:
    print(payment['product_id'], payment['amount'] / 10**18)

  for period, history in await client.archive.portfolio():
    print(period, history)
```

## Rewards And Competitions

The airdrop allocation and trading-competition leaderboards are public too:

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  airdrop = await client.rewards.ink_airdrop('0xYourWalletAddress')
  print(airdrop['amount'] / 10**18)

  contests = await client.rewards.leaderboard_contests(active=True)
  for contest in contests['contests']:
    track = contest['tracks'][0]
    board = await client.rewards.leaderboard(
      contest_id=contest['contest_id'], rank_type=track['rank_type'], limit=10
    )
    for position in board['positions']:
      print(position['subaccount'], position['account_value'])
```

Registering for a contest (`rewards.leaderboard_register`) is signed with your key.
