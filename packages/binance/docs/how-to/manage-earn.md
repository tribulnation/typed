# Query & Manage Earn Instruments

Simple Earn calls are signed — see [API Keys Setup](../api-keys.md). Examples below use the
Flexible product; Locked products (`client.spot.http.simple_earn.locked`) follow the same shape
with a fixed subscription duration.

## List Available Products

```python
from typed_binance import Binance

async with Binance.new() as client:
  products = await client.spot.http.simple_earn.flexible.list(asset='USDT')
  for product in products.get('rows', []):
    print(product.get('productId'), product.get('latestAnnualPercentageRate'))
```

## Subscribe

```python
from typed_binance import Binance

async with Binance.new() as client:
  subscription = await client.spot.http.simple_earn.flexible.subscribe(
    product_id='USDT001', amount='10',
  )
  print(subscription.get('purchaseId'))
```

## View Your Positions

```python
from typed_binance import Binance

async with Binance.new() as client:
  positions = await client.spot.http.simple_earn.flexible.position(asset='USDT')
  for position in positions.get('rows', []):
    print(position.get('productId'), position.get('totalAmount'))
```

## Redeem

```python
from typed_binance import Binance

async with Binance.new() as client:
  redemption = await client.spot.http.simple_earn.flexible.redeem(
    product_id='USDT001', redeem_all=True,
  )
  print(redemption.get('redeemId'))
```

`redeem_all=True` redeems the full position; otherwise pass `amount`.
`client.spot.http.simple_earn.locked` follows the same list/subscribe/position/redeem shape for
Locked products. `client.spot.http.staking` (ETH, SOL, and on-chain-yields staking) covers its own
products with `stake`/`redeem`/`account`/`quota` instead — e.g.
`client.spot.http.staking.eth.stake(amount=0.1)`.
