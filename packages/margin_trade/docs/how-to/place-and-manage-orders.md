# Place & Manage Orders

Orders go through `client.exchange`, signed by your master key or an approved agent (see
[Authenticated Setup](../authenticated-setup.md)). Reads go through `client.info`, keyed by
the account address. The examples use testnet.

## Place An Order

An order names its market by asset index `a` (the market's `index` field in
`info.meta()['universe']`, not its position in the list), its
side as `b` (true buys), its limit price `p`, size `s`, reduce-only flag `r` and type `t`.
Prices and sizes take a `Decimal` or a string.

```python
import os
from decimal import Decimal
from typed_margin_trade import MarginTrade

async with MarginTrade.new(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'], mainnet=False) as client:
  index = {m['name']: m['index'] for m in (await client.info.meta())['universe']}

  result = await client.exchange.order(
    [{'a': index['BTC'], 'b': True, 'p': Decimal('60000'), 's': Decimal('0.001'), 'r': False,
      't': {'limit': {'tif': 'Alo'}}}],
    grouping='na',
  )
  for status in result['statuses']:
    if 'resting' in status:
      print('resting', status['resting']['oid'])
    elif 'filled' in status:
      print('filled', status['filled']['avgPx'])
    else:
      print('refused', status['error'])
```

`tif` is `Gtc`, `Ioc`, `Alo` (post-only) or `FrontendMarket` (the market-order flavour the
web app sends). One request can carry several orders; each gets
its own entry in `statuses`, and a refused order is reported there rather than raised. Add
`'c': '0x...'` (32 hex digits) to give an order your own client id.

## List Open Orders

```python
import os
from typed_margin_trade import MarginTrade, Wallet

wallet = Wallet.parse(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'])

async with MarginTrade.new(wallet, mainnet=False) as client:
  orders = await client.info.open_orders(user=wallet.address)
  for order in orders:
    print(order['oid'], order['coin'], order['side'], order['limitPx'], order['sz'])
```

`info.frontend_open_orders` adds trigger and TP/SL details.

## Query One Order

```python
import os
from typed_margin_trade import MarginTrade, Wallet

wallet = Wallet.parse(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'])

async with MarginTrade.new(wallet, mainnet=False) as client:
  found = await client.info.order_status(user=wallet.address, oid=38288057415)
  if 'order' in found:
    print(found['order']['status'])
```

`order_status` and `historical_orders` lag the book by a few seconds: a just-placed order
can read `not found`, and a just-canceled one `open`. To know what is resting right now,
use `open_orders` (or the `order_updates` stream).

## Modify An Order

```python
import os
from decimal import Decimal
from typed_margin_trade import MarginTrade

async with MarginTrade.new(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'], mainnet=False) as client:
  index = {m['name']: m['index'] for m in (await client.info.meta())['universe']}
  result = await client.exchange.modify(
    38288057415,
    order={'a': index['BTC'], 'b': True, 'p': Decimal('59000'), 's': Decimal('0.001'), 'r': False,
           't': {'limit': {'tif': 'Alo'}}},
  )
```

A modified order rests under a new order id, reported in `statuses`. `batch_modify` changes
several orders in one request.

## Cancel Orders

```python
import os
from typed_margin_trade import MarginTrade, Wallet

wallet = Wallet.parse(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'])

async with MarginTrade.new(wallet, mainnet=False) as client:
  index = {m['name']: m['index'] for m in (await client.info.meta())['universe']}
  result = await client.exchange.cancel([{'a': index['BTC'], 'o': 38288057415}])
  print(result['statuses'])  # ['success'] or ['order not found']

  await client.exchange.cancel_by_cloid([{'asset': index['BTC'], 'cloid': '0x0000000000000000000000000000abcd'}])

  remaining = await client.info.open_orders(user=wallet.address)
```

There is no cancel-all action: list `open_orders` and cancel them in one `cancel` request.

```python
import os
from typed_margin_trade import MarginTrade, Wallet

wallet = Wallet.parse(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'])

async with MarginTrade.new(wallet, mainnet=False) as client:
  index = {m['name']: m['index'] for m in (await client.info.meta())['universe']}
  orders = await client.info.open_orders(user=wallet.address)
  if orders:
    await client.exchange.cancel([{'a': index[o['coin']], 'o': o['oid']} for o in orders])
```

## Leverage

```python
import os
from typed_margin_trade import MarginTrade

async with MarginTrade.new(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'], mainnet=False) as client:
  index = {m['name']: m['index'] for m in (await client.info.meta())['universe']}
  await client.exchange.update_leverage(asset=index['BTC'], is_cross=True, leverage=2)
```
