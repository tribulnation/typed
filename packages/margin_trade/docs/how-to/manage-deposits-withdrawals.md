# Manage Deposits & Withdrawals

Margin Trade holds USDC (on Solana) and PRL (on the Pearl chain). You deposit by sending the
token to your account's custody address, and withdraw with a signed `exchange.withdraw`.
The examples use testnet.

## Deposit Address

```python
import os
from typed_margin_trade import MarginTrade

async with MarginTrade.new(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'], mainnet=False) as client:
  usdc = await client.user.get_deposit_address(asset='USDC', chain='solana')
  prl = await client.user.get_deposit_address(asset='PRL', chain='pearl')
  print(usdc['depositAddress'], prl['depositAddress'])
```

Sending the token to that address credits the account. To check what your Solana wallet
holds before depositing, `solana.get_onchain_asset(account=..., asset='USDC')` reads its
on-chain balance.

## Withdraw

`amount` is in raw micro-units (6 decimals) as an integer string: `'10000000'` is 10 USDC.
The USDC minimum is 2 USDC, and a flat 1 USDC fee is deducted from the amount.

```python
import os
from typed_margin_trade import MarginTrade, Wallet

wallet = Wallet.parse(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'])

async with MarginTrade.new(wallet, mainnet=False) as client:
  await client.exchange.withdraw(destination=wallet.address, amount='2000000')
```

A withdrawal settles asynchronously, so `withdraw` returns nothing; follow it in the
transfer history. Only the master key can withdraw: an agent client raises `AuthError`
without sending.

## Move Between Perp And Spot

`amount` is in micro-USDC, as a whole-number string (the same unit as `withdraw`):
`'1000000'` moves 1 USDC, `'1'` only 0.000001 USDC. Sign with the master key: an agent
cannot move the master's funds between wallets, and the client refuses the call with
`AuthError` before sending it.

```python
import os
from typed_margin_trade import MarginTrade

async with MarginTrade.new(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'], mainnet=False) as client:
  await client.exchange.usd_class_transfer('1000000', to_perp=False)  # 1 USDC perp -> spot
  await client.exchange.usd_class_transfer('1000000', to_perp=True)  # 1 USDC spot -> perp
```

## History

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  transfers = await client.user.get_transfer_history(address)
  for item in transfers['items']:
    print(item['type'], item['status'], item['asset'], item['amount'], item['fee'])

  deposits = await client.info.deposit_history(address)
  withdrawals = await client.info.withdrawal_history(address)
```

`get_transfer_history` covers deposits, withdrawals, liquidations, perp/spot transfers and
system payouts in one list, with each item's status (`Completed`, `Processing`, `Failed`).

## Testnet Faucet

On testnet, `user.faucet_claim()` credits test USDC once per UTC day instead of a deposit.
