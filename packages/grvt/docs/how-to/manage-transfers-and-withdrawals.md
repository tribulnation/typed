# Manage Transfers & Withdrawals

Funds arrive in your funding (main) account, move between it and your trading
sub-accounts by transfer, and leave by withdrawal. Transfers and withdrawals are signed with
the signer private key, and GRVT only accepts them from an API key with the matching
transfer or withdrawal permission (see [API Keys Setup](../api-keys.md)). Without it, GRVT
answers code `1001` and the client raises `AuthError`. `withdrawal_fee` needs the
withdrawal permission too.

They move real funds, so try each one with a small amount on testnet before using it in
production.

## Deposit Addresses

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  addresses = await client.edge.deposit_addresses()
  for chain in addresses['chains']:
    tokens = [token['name'] for token in chain['supported_tokens']]
    print(chain['chain'], chain['deposit_address'] or '(not generated)', tokens)

  generated = await client.edge.generate_deposit_address('TRON_TEST')
  print(generated['deposit_address'])
```

Some chains have no address until you generate one; pass the `chain` name exactly as
`deposit_addresses()` returns it.

## Transfer Between Accounts

```python
from decimal import Decimal
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  funding = await client.trading.funding_account_summary()
  main_account = funding['result']['main_account_id']
  subs = await client.trading.sub_accounts()
  print(subs['sub_account_ids'])  # your trading sub-accounts
  trading_account = subs['sub_account_ids'][0]  # the one to fund

  ack = await client.trading.transfer(
    from_account_id=main_account,
    from_sub_account_id='0',
    to_account_id=main_account,
    to_sub_account_id=trading_account,
    currency='USDT',
    num_tokens=Decimal('100'),
    transfer_type='STANDARD',
    transfer_metadata='',
    from_wallet_type='FUNDING',
    to_wallet_type='FUTURES',
  )
  print(ack)
```

These are the fields GRVT records for a funding-to-trading transfer in `transfer_history`.
Sub-account `'0'` is the funding account itself; swap the two sides (and wallet types) to
move funds back. GRVT also allows transfers to another main account you have allowlisted.

A transfer names both sub-accounts itself: the account-level key it needs has no
sub-account of its own, and `sub_accounts()` lists the ones it can reach.

## Withdraw

```python
from decimal import Decimal
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  currencies = await client.market.currency()
  usdt = next(c for c in currencies if c['symbol'] == 'USDT')
  fee = await client.trading.withdrawal_fee(usdt['id'])
  print(fee['withdrawal_fee'])

  funding = await client.trading.funding_account_summary()
  await client.trading.withdrawal(
    from_account_id=funding['result']['main_account_id'],
    to_eth_address='0xYourEthereumAddress',
    currency='USDT',
    num_tokens=Decimal('50'),
  )
```

`withdrawal_fee` takes GRVT's numeric currency id, so look it up by symbol as above rather
than hard-coding it. Per GRVT, withdrawals bridge to Ethereum and take time to settle, with a
minimum amount (unless you withdraw your whole balance) and a flat fee. Check both before
withdrawing.

For other chains GRVT offers a third-party bridge: `client.edge.bridge_withdrawal_info` lists
its routes, `bridge_withdrawal_quote` returns a firm quote, and `bridge_withdrawal_status`
follows a bridge withdrawal by its quote id. The client gets quotes and tracks status, but
does not submit a bridge withdrawal.

## History

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  deposits = await client.trading.deposit_history()
  withdrawals = await client.trading.withdrawal_history()
  transfers = await client.trading.transfer_history(['USDT'])
  for transfer in transfers['result']:
    print(
      transfer['event_time'],
      transfer['num_tokens'],
      transfer['from_wallet_type'],
      transfer['to_wallet_type'],
    )
  print(len(deposits['result']), len(withdrawals['result']))
```

Leave `currency` out for every currency, or pass a list of symbols to narrow it. Each call
returns one page; use the `_paged` variants for the full history (see
[Paginate Through Results](paginate-through-results.md)). To follow new
funding events live, subscribe to `client.trading_streams.transfers`, `deposits` or
`withdrawals`.
