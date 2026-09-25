# Transfers & Sub-Accounts

A wallet's master account can create sub-accounts and move assets between them, and between
the perps and spot sides of each account. Every amount is an integer in the asset's
smallest unit: `asset_details` gives each asset's `decimals` (USDC has 6, ETH and LIT 8).

## Create A Sub-Account

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  receipt = await client.tx.create_sub_account()
```

The new account's index is not in the transaction receipt. List the wallet's accounts to
find it; the master account comes first:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  accounts = await client.api.account.by_l1_address(l1_address='0x0000000000000000000000000000000000000000')
  master, *subs = accounts['sub_accounts']
  print(master['index'], [sub['index'] for sub in subs])
```

Sub-accounts cannot be deleted. Each one has its own API key slots: register a key on it
with `change_api_key` from a client built for that account index
([Authenticated Setup](../authenticated-setup.md)).

## Transfer Between Accounts

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  account = client.signer.account_index
  fee = await client.api.account.transfers.fee_info(account_index=account, to_account_index=281474976710578)

  await client.tx.transfer(
    to_account_index=281474976710578,
    amount=50_000_000,                      # 50 USDC
    usdc_fee=fee['transfer_fee_usdc'],
  )
```

Without `asset_index` a transfer moves USDC (asset `3`), perps side to perps side. Pass
`asset_index`, `from_route` and `to_route` (`'perps'` or `'spot'`) for anything else.
Transfers inside one master account need only the API key; a transfer to an account owned
by another wallet also needs the Ethereum key (`LIGHTER_ETH_PRIVATE_KEY`), which the client
applies automatically when configured.

## Withdraw

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  await client.tx.withdraw(amount=10_000_000)  # 10 USDC to the owning wallet

  pool = await client.api.account.transfers.fast_withdraw_info(client.signer.account_index)
  await client.tx.fast_withdraw(
    '0x0000000000000000000000000000000000000000',
    amount=10_000_000,
    to_account_index=pool['to_account_index'],
  )
```

`withdraw` pays the owning wallet through the slow, secure path. `fast_withdraw` pays
USDC to any address from Lighter's fast-withdrawal pool, within the pool's current
`max_withdrawal_amount`; it needs the Ethereum key and goes over HTTP only.

## History

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  account = client.signer.account_index
  transfers = await client.api.account.transfers.history_paged(account)
  withdrawals = await client.api.account.transfers.withdrawals_paged(account)
  deposits = await client.api.account.transfers.deposits_paged(
    account, l1_address='0x0000000000000000000000000000000000000000'
  )
  for deposit in deposits:
    print(deposit['timestamp'], deposit['amount'], deposit['status'])
```

## Deposit From Other Chains

`client.deposit_bridge` creates universal deposit addresses on other chains that credit a
Lighter account. It needs a bridge API key that Lighter issues to builders
(`LIGHTER_BRIDGE_API_KEY`):

```python
from typed_lighter import Lighter

async with Lighter.new(public=True, bridge_api_key='...') as client:
  address = await client.deposit_bridge.create_address(
    '0x0000000000000000000000000000000000000000', market='perps', asset='USDC'
  )
  status = await client.deposit_bridge.status('0x0000000000000000000000000000000000000000')
```

Upstream reference: [Deposits, transfers and withdrawals](https://apidocs.lighter.xyz/docs/deposits-transfers-and-withdrawals).
