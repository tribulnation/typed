# Fetch Account Data

These calls are signed by your API wallet. See [Authenticated Setup](../authenticated-setup.md).

## Balances

```python
from typed_aster import Aster

async with Aster.new() as client:
  for balance in await client.futures.account.balance():
    print(balance['asset'], balance['availableBalance'])

  spot = await client.spot.account.info()
  for asset in spot['balances']:
    print(asset['asset'], asset['free'], asset['locked'])
```

`client.prediction.account.info()` returns the prediction-market balances the same way.

## Futures Account And Positions

```python
from typed_aster import Aster

async with Aster.new() as client:
  account = await client.futures.account.info()
  print(account['totalWalletBalance'], account['availableBalance'])

  for position in await client.futures.position.risk('BTCUSDT'):
    print(position['symbol'], position['positionAmt'], position['unRealizedProfit'])
```

## Account Settings

```python
from typed_aster import Aster

async with Aster.new() as client:
  mode = await client.futures.account.position_mode()
  await client.futures.account.set_leverage('BTCUSDT', leverage=5)
  await client.futures.account.set_margin_type('BTCUSDT', margin_type='ISOLATED')
  fees = await client.futures.account.commission_rate('BTCUSDT')
  print(mode, fees)
```

## Trade And Income History

```python
from typed_aster import Aster

async with Aster.new() as client:
  fills = await client.futures.trade.user_trades('BTCUSDT', limit=50)
  income = await client.futures.account.income(income_type='FUNDING_FEE')
  spot_fills = await client.spot.trade.user_trades('ASTERUSDT')
  history = await client.spot.account.transaction_history(asset='USDT')
  print(fills, income, spot_fills, history)
```

Without a time range, these return the last 7 days. For longer ranges, use the `_paged`
variants in [Paginate Through Results](paginate-through-results.md).

## On-Chain State By Address

Aster Chain's read-only JSON-RPC takes any address and needs no credentials:

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  address = '0x...any-aster-account'
  state = await client.chain.rpc.get_balance(address=address, block_tag='latest')
  orders = await client.chain.rpc.open_orders(address=address, block_tag='latest')
  fills = await client.chain.rpc.user_fills(address=address, block_tag='latest')
  print(state['accountPrivacy'], orders, fills)
```

An account in private mode (`client.chain.account.modify_status`) reveals less here.
