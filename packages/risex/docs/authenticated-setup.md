# Authenticated Setup

RISEx has no exchange-issued API keys. Every write is an EIP-712 signature, and the client produces all of them for you from two EVM private keys:

| Key | Signs | Environment variable |
| --- | --- | --- |
| Account key (the wallet holding collateral) | registering or revoking signers, OperatorHub allowances | `RISEX_ACCOUNT_KEY` |
| Signer key (a session key registered to the account) | orders, cancels, leverage and margin changes, logins, WebSocket auth | `RISEX_SIGNER_KEY` |
| Account address (not a secret) | which account a signer-only client trades for | `RISEX_ACCOUNT` |

Either key alone is useful: the account key can register a signer, and the signer key plus `RISEX_ACCOUNT` can trade. Calls that need a JWT log in and refresh on their own: `account.fees`, every `affiliate` read, `auth.allowance`, `auth.sessions`, `auth.revoke_session` and `auth.logout`, `orders.tpsl.place`, `cancel` and `cancel_all`, `points.wallet` and `points.history` (only for your own address), and `stats.wallet_count`. On a `public=True` client they raise `AuthError`.

Mainnet accounts are invite-only (public market data needs nothing); testnet is open and self-service. The client defaults to `network='mainnet'`; pass `network='testnet'` to use testnet.

## 1. Generate keys

```python
from eth_account import Account

account, signer = Account.create(), Account.create()
print(f'RISEX_ACCOUNT_KEY="{account.key.hex()}"')
print(f'RISEX_SIGNER_KEY="{signer.key.hex()}"')
```

Save both lines to a `.env` file and keep it out of version control.

## 2. Claim test USDC

The testnet faucet funds the account and registers it on-chain. No signature is needed.

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  assert client.credentials is not None
  await client.account.deposit(account=client.credentials.account, amount='1000')
```

## 3. Register the signer

Registering needs both keys: the account authorizes the signer and the signer countersigns. It is valid for 30 days unless you pass `expiration`.

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  result = await client.auth.register_signer(label='my-bot')
  print(result['success'], result['status'])  # True 1 (active)
```

## 4. Trade with the signer

From here on, the signer key is enough. Keep the account key offline and set only:

```bash
RISEX_SIGNER_KEY="0x..."
RISEX_ACCOUNT="0xYourAccountAddress"
```

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  fees = await client.account.fees()  # JWT login happens on first use
  print(fees['tier'])
```

To pass keys explicitly instead of through the environment, use `RISEx.new(account_key=..., signer_key=..., account=...)`. Explicit arguments replace the environment as a whole.

To revoke a signer, call `await client.auth.revoke_signer(signer_address)` with the account key configured.
