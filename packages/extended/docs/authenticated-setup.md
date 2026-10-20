# Authenticated Setup

Extended runs on Starknet. Private calls carry an **API key**; orders, transfers and
withdrawals are additionally signed with the sub-account's **Stark private key** for its
**vault**. All three values are shown on the API management page of the Extended web app,
per sub-account.

## Three Modes

| Mode | Needs | Can do |
| --- | --- | --- |
| Public | nothing (`public=True`) | market data, vault, public streams |
| Read-only | API key | account reads, cancels, leverage, account stream |
| Signing | API key + Stark private key + vault | everything, including orders, transfers and withdrawals |

## Environment Variables

```bash
# .env
EXTENDED_API_KEY="your_api_key"
EXTENDED_STARK_PRIVATE_KEY="0x..."
EXTENDED_VAULT="123456"
# optional: checked against the private key when set
EXTENDED_STARK_PUBLIC_KEY="0x..."
```

```python
from dotenv import load_dotenv
from typed_extended import Extended

load_dotenv()

async with Extended.new() as client:
  info = await client.account.info()
  print(info['accountId'], info['status'])
```

Leave out the Stark variables for a read-only client. Arguments override the environment:

```python
from typed_extended import Extended

client = Extended.new(
  api_key='your_api_key',
  stark_private_key='0x...',
  vault=123456,
)
```

## Public Access

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  markets = await client.info.markets(['BTC-USD', 'ETH-USD'])
```

## Mainnet vs Testnet

`network='testnet'` targets Extended on Starknet Sepolia and reads the same variables with an
`EXTENDED_TESTNET_` prefix (`EXTENDED_TESTNET_API_KEY`, ...). Testnet keys are created in the
testnet web app.

```python
from typed_extended import Extended

async with Extended.new(network='testnet') as client:
  balance = await client.account.balance()
```

## Faster Signing

`pip install "typed-extended[fast]"` adds a native Stark backend, picked automatically when
installed. Force one with `Extended.new(stark_backend='python')`.

A missing API key, a Stark key without a vault, or a public key that doesn't match the
private key raises `AuthError` when the client is built.
