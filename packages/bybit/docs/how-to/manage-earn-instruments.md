# Manage Earn Instruments

`client.http.finance` covers Bybit's earn products: `fixed_saving`, `easy_onchain`,
`hold_to_earn`, `advanced_earn`, and `byusdt`. They share the same list/position/subscribe/redeem
shape; this guide works through `fixed_saving` as the worked example. Listing products is
public; everything else needs credentials — see [API Keys Setup](../api-keys.md).

## List Available Products

`finance.fixed_saving.product` needs no authentication:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  products = await client.http.finance.fixed_saving.product(coin='USDT')
  for product in products['list']:
    print(product['productId'], product['category'], product['duration'], product['status'])
```

Omit `coin` to list every coin's products. `category` is one of `'FixedTermSaving'`,
`'FundPool'`, or `'FundPoolPremium'` — only `'FundPool'` positions support early redemption.

## List Your Positions

`finance.fixed_saving.position` requires the API key's "Earn" permission:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  positions = await client.http.finance.fixed_saving.position(category='FundPool')
  for position in positions['list']:
    print(position['positionId'], position['coin'], position['amount'], position['status'])
```

Filter with `product_id` and/or `coin` instead of `category` to narrow further; all three are
optional and combine as filters.

## Subscribe

`finance.fixed_saving.place_order` takes one request dict and stakes into a product. Supply your
own `orderLinkId`, up to 36 characters, as an idempotency key — Bybit rejects the call if you
reuse one:

```python
import uuid
from typed_bybit import Bybit

async with Bybit.new() as client:
  order = await client.http.finance.fixed_saving.place_order({
    'productId': '10001',
    'category': 'FundPool',
    'coin': 'USDT',
    'amount': '100',
    'accountType': 'UNIFIED',
    'orderLinkId': str(uuid.uuid4()),
  })
  print(order['orderId'], order['orderLinkId'])
```

`accountType` is `'FUND'` or `'UNIFIED'` and picks which wallet funds the stake. Get `productId`
from `finance.fixed_saving.product`.

## Redeem Early

`finance.fixed_saving.redeem` only works on a `'FundPool'` position — `FixedTermSaving` and
`FundPoolPremium` positions run to maturity instead:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  redemption = await client.http.finance.fixed_saving.redeem({
    'productId': '10001',
    'category': 'FundPool',
    'positionId': '20001',
  })
  print(redemption['redeemAmount'], redemption['estEarnings'])
```

Both fields in the result are estimates: the redeemed principal and the earnings paid out at
the early-redemption APY, which is usually lower than the product's full-term rate.
