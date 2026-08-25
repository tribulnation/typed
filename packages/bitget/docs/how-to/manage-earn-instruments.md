# Manage Earn Instruments

Bitget's Earn product on UTA is **Elite**, structured/subscription products. All of these are
authenticated.

## List Products & Holdings

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  products = await client.uta.earn.elite.products()
  holdings = await client.uta.earn.elite.assets()
```

## Subscribe

Look up current subscription terms for a product, then subscribe using its `productSubId`:

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  products = await client.uta.earn.elite.products()
  info = await client.uta.earn.elite.subscribe_info(product_id=products[0]['productId'])
  result = await client.uta.earn.elite.subscribe({
    'productSubId': info['productSubId'],
    'amount': 10.0,
    'paymentAccount': 'unified',
  })
```

## Redeem

Same pattern, with a redemption mode chosen from the terms:

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  products = await client.uta.earn.elite.products()
  info = await client.uta.earn.elite.redeem_info(product_id=products[0]['productId'])
  await client.uta.earn.elite.redeem({
    'productId': info['productId'],
    'productSubId': info['productSubId'],
    'redeemType': 'fast',
    'amount': 10.0,
    'receiveAccount': 'unified',
  })
```

## Subscription / Redemption / Interest Records

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  records = await client.uta.earn.elite.records(type='subscribe')
```

Paged, see [Paginate Through Results](paginate-through-results.md).

## Classic v2

Classic exposes Elite plus two more standalone products under `client.classic.earn`: Savings
(`savings_products`, `savings_subscribe`, `savings_redeem`) and SharkFin
(`sharkfin_products`, `sharkfin_subscribe`). SharkFin is a fixed-term instrument that redeems
itself automatically at maturity, so there's no manual redeem call for it.
