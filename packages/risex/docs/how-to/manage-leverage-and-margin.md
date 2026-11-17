# Manage Leverage & Margin

Leverage and margin settings are per market and signed by the signer key, like orders (see [Authenticated Setup](../authenticated-setup.md)). Gas is paid by RISEx.

## Set Leverage

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  result = await client.account.update_leverage(1, leverage='10')
  print(result['receipt']['status'])  # 1 on success
```

`leverage` is a whole number as a string, up to the market's `config['max_leverage']`.

## Switch Margin Mode

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  await client.account.update_margin_mode(1, margin_mode=1)  # isolated
  await client.account.update_margin_mode(1, margin_mode=0)  # back to cross
```

## Adjust Isolated Margin

For an isolated position, add or remove margin. `amount` is USDC in 18-decimal integer units, as a string; a negative amount removes margin.

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  await client.account.update_isolated_margin(1, amount=str(5 * 10**18))  # add 5 USDC
```

## Check The Result

```python
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'

async with RISEx.new(network='testnet') as client:
  result = await client.account.position(1, account=ACCOUNT)
  position = result['position']
  print(position['leverage'], position['margin_mode'], position['isolated_usdc_balance'])
```

Before placing an order, `client.portfolio.detail_preview(...)` shows how it would change margin and risk.
