# Transfer & Withdraw

Transfers and withdrawals are signed with your Stark key, so they need a
[signing client](../authenticated-setup.md). Deposits are made on-chain, from the Extended web
app; their history shows up in asset operations below.

## Transfer Between Sub-Accounts

```python
from decimal import Decimal
from typed_extended import Extended

async with Extended.new() as client:
  me = await client.account.info()
  subs = await client.account.sub_accounts()
  target = next(sub for sub in subs if sub['accountId'] != me['accountId'])
  result = await client.funds.transfer(
    from_account=me['accountId'],
    to_account=target['accountId'],
    amount=Decimal('10'),
    transferred_asset='USD',
  )
  print(result['id'], result['validSignature'])
```

Both sub-accounts must belong to the same wallet, and the client must hold the sending
sub-account's API key, Stark key and vault: to move funds back, build a client with the other
sub-account's credentials. The client looks up the receiving vault and key itself.

## Withdraw To Starknet

Starknet-wallet accounts can withdraw straight to a Starknet address:

```python
from decimal import Decimal
from typed_extended import Extended

async with Extended.new() as client:
  withdrawal_id = await client.funds.withdraw(
    {
      'chainId': 'STRK',
      'amount': Decimal('25'),
      'asset': 'USD',
      'recipient': '0x0123...',
    }
  )
```

## Withdraw To An EVM Chain

EVM-wallet accounts withdraw through the bridge: list the supported chains, request a quote,
commit it, then withdraw with its id.

```python
from decimal import Decimal
from typed_extended import Extended

async with Extended.new() as client:
  config = await client.funds.bridge_config()
  print([chain['chain'] for chain in config['chains']])  # ARB, ETH, BASE, ...
  quote = await client.funds.bridge_quote(
    chain_in='STRK', chain_out='ARB', amount=Decimal('25')
  )
  print(quote['fee'])
  await client.funds.commit_quote(quote['id'])
  withdrawal_id = await client.funds.withdraw(
    {
      'chainId': 'ARB',
      'amount': Decimal('25'),
      'asset': 'USD',
      'quoteId': quote['id'],
    }
  )
```

`asset` is the collateral asset `USD` or an active tradable spot asset. A `STRK` withdrawal
needs `recipient`; a bridge withdrawal needs `quoteId` and signs to the account's bridge
address unless you pass `recipient`.

## Deposit, Withdrawal And Transfer History

```python
from typed_extended import Extended

async with Extended.new() as client:
  operations = await client.account.asset_operations_paged(
    type=['DEPOSIT', 'WITHDRAWAL', 'TRANSFER']
  )
  for operation in operations:
    print(
      operation['time'],
      operation['type'],
      operation['status'],
      operation['amount'],
      operation['fee'],
    )
```
