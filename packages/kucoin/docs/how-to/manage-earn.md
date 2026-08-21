# Query & Manage Earn Instruments

KuCoin's Earn products — flexible/fixed savings, staking (general, KCS, ETH),
dual investment, and promotions — share one purchase/redeem flow under `client.earn`.
These calls need credentials — see [API Keys Setup](../api-keys.md).

## List Products

Each product family has its own listing call:

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  savings = await client.earn.savings_products(currency='USDT')
  staking = await client.earn.staking_products(currency='USDT')
  dual = await client.earn.dual_investment_products(category='DUAL_CLASSIC')
  for product in savings:
    print(product['id'], product['currency'], product['returnRate'])
```

`earn.kcs_staking_products`, `earn.eth_staking_products` and `earn.promotion_products`
cover the remaining families.

## List Your Holdings

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  holdings = await client.earn.account_holding(currency='USDT')
  for holding in holdings['items']:
    print(holding['orderId'], holding['productType'], holding['holdAmount'])
```

Use `earn.account_holding_paged` to walk every page automatically — see
[Paginate Through Results](paginate-through-results.md).

## Subscribe To A Product

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  savings = await client.earn.savings_products(currency='USDT')
  result = await client.earn.purchase({
    'productId': savings[0]['id'],
    'amount': '10',
    'accountType': 'TRADE',
  })
  print(result['orderId'])
```

## Redeem A Holding

Preview a redemption before submitting it — early redemption of a fixed-term holding
can carry an interest penalty:

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  order_id = 'holding-order-id'
  preview = await client.earn.redeem_preview(order_id=order_id)
  print(preview['redeemAmount'], preview['penaltyInterestAmount'])

  redeemed = await client.earn.redeem(order_id=order_id, amount='10')
  print(redeemed['status'])
```
