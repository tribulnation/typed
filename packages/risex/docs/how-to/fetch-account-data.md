# Fetch Account Data

Account reads on RISEx are keyed by address and need no signature, so they work on a public client for any account. Replace `ACCOUNT` with your account address.

## Balances

```python
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'

async with RISEx.new(public=True) as client:
  config = await client.system.config()
  usdc = await client.account.balance(account=ACCOUNT, token=config['addresses']['usdc'])
  cross = await client.account.cross_margin_balance(ACCOUNT)
  print(usdc['balance'], cross['balance'])
```

`cross_margin_balance` is the collateral balance plus unrealized PnL from cross-margin positions.

## Portfolio Summary

```python
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'

async with RISEx.new(public=True) as client:
  details = await client.portfolio.details(ACCOUNT)
  summary = details['summary']
  print(summary['total_account_value'], summary['free_collateral'], summary['margin_usage'], summary['risk_level'])
```

`client.portfolio` also has PnL, equity and volume charts, a PnL calendar, realized PnL history and trading stats.

## Positions

```python
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'

async with RISEx.new(public=True) as client:
  result = await client.account.positions(account=ACCOUNT)
  for position in result['positions']:
    print(position)
  btc = await client.account.position(1, account=ACCOUNT)
  print(btc['position']['size'], btc['position']['leverage'], btc['position']['margin_mode'])
```

`positions` lists open positions only; `position` returns one market's position, including the leverage and margin mode set for it even when it is flat.

`positions` returns the raw on-chain values: `size`, `quote_amount`, `avg_entry_price`, `leverage`, `isolated_usdc_balance` and `last_funding_payment` are `int`s scaled by 10^18, so a `size` of `-655000000000000000` is a 0.655 short. Divide by `10**18` as a `Decimal` to read them exactly:

```python
from decimal import Decimal
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'
WAD = Decimal(10**18)

async with RISEx.new(public=True) as client:
  result = await client.account.positions(account=ACCOUNT)
  for position in result['positions']:
    print(position['market_id'], position['size'] / WAD, position['avg_entry_price'] / WAD, position['leverage'] / WAD)
```

`position` and `portfolio.details` (whose `positions` also carry mark price, unrealized PnL and liquidation price) return plain decimals and need no conversion; a field with no value (such as `liquidation_price` on a flat position) is the empty string `''` rather than a `Decimal`.

## Trade, Funding And Transfer History

```python
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'

async with RISEx.new(public=True) as client:
  trades = await client.account.trade_history(ACCOUNT, market_id=1, limit=50)
  funding = await client.account.funding_payments(ACCOUNT, limit=50)
  transfers = await client.account.transfer_history(account=ACCOUNT, type='DEPOSIT')
  print(len(trades['trades']), len(funding['records']), len(transfers['items']))
```

Every history accepts `datetime` bounds (`start_time`/`end_time`, or `block_time_from`/`block_time_to` for transfers) and paginates; see [Paginate Through Results](paginate-through-results.md).

## Fees And Signers

Your fee tier needs a login, which the client performs with your keys (see [Authenticated Setup](../authenticated-setup.md)):

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  fees = await client.account.fees()
  print(fees['tier'])
  assert client.credentials is not None and client.credentials.signer is not None
  status = await client.auth.session_key_status(account=client.credentials.account, signer=client.credentials.signer)
  print(status['status_description'])
```
