# Authenticated Setup

Nado has no API keys. Your identity is an EVM wallet, and every write — placing or
cancelling an order, withdrawing, transferring, minting or burning NLP, linking a signer,
liquidating a subaccount, registering for a trading competition — is an EIP-712 signature
the client computes for you. Almost every read needs no credentials, so
`Nado.new(public=True)` covers market data and any subaccount's account data. The
exceptions are `trigger.list_trigger_orders` (and `list_trigger_orders_paged`), a signed
read of your own trigger orders, and the private `streams.order_update` stream, which
authenticates with your key.

## Signing Key

Put the wallet's private key in a `.env` file:

```bash
# .env
NADO_PRIVATE_KEY="0x..."          # mainnet (Ink)
NADO_TESTNET_PRIVATE_KEY="0x..."  # testnet (Ink Sepolia), optional
```

Each network reads its own variables, so a testnet key is never used on mainnet:

```python
from dotenv import load_dotenv
from typed_nado import Nado

load_dotenv()

async with Nado.new() as client:  # NADO_PRIVATE_KEY
  info = await client.gateway.subaccount_info()
  print(info['exists'], info['spot_balances'])

async with Nado.new(network='testnet') as client:  # NADO_TESTNET_PRIVATE_KEY
  print(await client.gateway.status())
```

You can also pass the key directly: `Nado.new(private_key='0x...')`.

A subaccount exists once the wallet has deposited collateral on Nado (deposits are
on-chain transactions, made in the Nado app or directly against the contracts). The client
acts for the `default` subaccount unless you set `NADO_SUBACCOUNT` or pass `subaccount=`.

## Linked Signer (Recommended For Bots)

Each subaccount can delegate signing to one linked signer: a separate key with full
permissions, including withdrawals. Keep the owner key cold and give the bot the linked key
plus the owner's address:

```bash
# .env
NADO_PRIVATE_KEY="0x..."     # the linked signer's key
NADO_ADDRESS="0x..."         # the owner wallet
```

Link a signer once, from a client holding the owner key:

```python
from typed_nado import Nado
from typed_nado.core import subaccount_bytes32

async with Nado.new() as client:
  await client.gateway.link_signer({'signer': subaccount_bytes32('0xDelegateAddress', 'default')})
  print(await client.gateway.linked_signer())
```

Only the first 20 bytes of `signer` matter. Changing or revoking the linked signer (all
zeros) cancels every resting order of that subaccount.

## Public Clients

`Nado.new(public=True)` skips credential resolution entirely. Any signed call on it raises
`AuthError` before anything is sent.
