# API Keys Setup

Gate DEX has no public endpoints and no testnet: every request, market data included, is
signed with an API key on mainnet. The client signs each request for you (HMAC-SHA256).

## Create A Key

1. Open the [Gate DEX developer console](https://web3.gate.com/api-manage) and log in by
   connecting a wallet.
2. Bind an email address and a phone number; Gate asks for both before the first key.
3. Create a key with a name, a passphrase and an IP allowlist. An account can hold up to 3
   keys.

The console then shows an **API Key (AK)** and a **Secret Key (SK)**. The passphrase only
protects viewing the SK in the console and is never sent with requests; without it, a lost
SK cannot be recovered. Requests from an IP outside the allowlist are rejected.

Gate's [developer console guide](https://gateweb3.gitbook.io/gate_dex_api/exploredexapi/en/api-access-and-usage/developer-console)
walks through the same steps.

## Environment Variables

```bash
# .env
GATE_DEX_API_KEY="your_api_key"
GATE_DEX_SECRET_KEY="your_secret_key"
```

```python
from dotenv import load_dotenv
from typed_gate_dex import GateDex

load_dotenv()

async with GateDex.new() as client:
  chains = await client.trade.chains()
  print([chain['chain_name'] for chain in chains])
```

## Direct Usage

Arguments take precedence over the environment:

```python
from typed_gate_dex import GateDex

client = GateDex.new(api_key='your_api_key', api_secret='your_secret_key')
```

A missing key or secret raises `AuthError` when the client is built, before any request.

## Rate Limits

Gate's free tier allows about one request per second per key; going faster raises
`RateLimited`. Higher tiers are arranged with Gate (see its
[API fees page](https://gateweb3.gitbook.io/gate_dex_api/exploredexapi/en/api-fees)).

## Clock

Each signature carries the current time, and Gate rejects one more than 30 seconds away
from its own clock with `AuthError` (code `10101`). Keep the host's clock synchronized.
