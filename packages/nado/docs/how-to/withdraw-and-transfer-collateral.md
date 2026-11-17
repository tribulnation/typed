# Withdraw & Transfer Collateral

Deposits are on-chain transactions on Ink (made in the Nado app or against the Nado
contracts), not API calls. Withdrawals and transfers between subaccounts are signed
executes, available on `client.gateway`.

## Check What You Can Withdraw

```python
from typed_nado import Nado

async with Nado.new() as client:
  limit = await client.gateway.max_withdrawable(product_id=0)  # 0 is USDT0
  print(limit['max_withdrawable'] / 10**18)

  fees = await client.gateway.fee_rates()
  print(fees['withdraw_sequencer_fees'][0] / 10**18)  # flat USDT0 withdrawal fee
```

Pass `spot_leverage=False` to see the limit without borrowing. Both values are x18.

## Withdraw

Withdrawal amounts use the token's native decimals, not x18: USDT0 has 6, so 25 USDT0 is
`25 * 10**6`.

> **Real funds:** this signs and executes on mainnet with real funds; try `Nado.new(network='testnet')` first.

```python
from typed_nado import Nado

async with Nado.new() as client:
  await client.gateway.withdraw_collateral({'productId': 0, 'amount': 25 * 10**6})
```

The funds go to the wallet that owns the subaccount, minus the flat fee.
`withdraw_collateral_v2` pays a dynamic fee instead (quote it with `dynamic_fee_quote`, cap
it with `max_fee_x18`) and can send to any address via `sendTo`; a non-zero `sendTo` must be
signed by the owner key, not a linked signer. Withdrawals appear in
`client.archive.events(..., event_types=['withdraw_collateral'])`.

## Transfer Between Subaccounts

> **Real funds:** this signs and executes on mainnet with real funds; try `Nado.new(network='testnet')` first.

```python
from typed_nado import Nado
from typed_nado.core import subaccount_bytes32

async with Nado.new() as client:
  other = subaccount_bytes32('0xYourWalletAddress', 'savings')
  await client.gateway.transfer_quote({'recipient': other, 'amount': 10 * 10**18})
```

Transfers move USDT0 in x18 units (at least 5 USDT0), are charged a flat fee, and a wallet
can send to at most 5 new recipients per 24 hours.

## Deposit Address

Each subaccount has a direct-deposit address: tokens sent there are credited to it.

```python
from typed_nado import Nado

async with Nado.new() as client:
  address = await client.archive.direct_deposit_address()
  print(address['v1_address'])
```
