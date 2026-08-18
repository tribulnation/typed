# Fetch Earn & Asset Data

Use `Bit2Me.new()` for the authenticated asset and earn surfaces in this package.

## Fetch Earn APY

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  apy = await client.v2.earn.apy()
  print(list(apy.keys())[:3])
```

## Fetch Earn Assets

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  assets = await client.v2.earn.assets()
  print(assets[0]['currency'])
```

## Fetch Earn Wallets

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  wallets = await client.v2.earn.wallets(limit=20)
  print(wallets['data'][0]['currency'])
```

## Fetch Currency Assets

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  assets = await client.v2.currency.assets.list()
  print(assets['BTC']['name'])
```
