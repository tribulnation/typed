# API Keys Setup

Etherscan issues one API key per account, from the **API Keys** section of your
[Etherscan account](https://etherscan.io/myapikey). The same key authenticates every chain
the V2 API covers — there is no per-chain key. The free tier covers most of this client's
surface; a handful of endpoints (bulk exports, extended historical stats, some NFT/token
lookups) require a paid Etherscan plan and return an explicit "Pro endpoint" or "Exclusive
endpoint" message on the free tier.

## Environment Variables

```bash
# .env
ETHERSCAN_API_KEY="your_api_key"
ETHERSCAN_RATE_LIMIT="4"
```

`ETHERSCAN_API_KEY` is required for everything except `usage.chain_list`. `ETHERSCAN_RATE_LIMIT`
is optional — see Rate Limiting below.

## Using It

```python
from dotenv import load_dotenv
from typed_etherscan import Etherscan

load_dotenv()

async with Etherscan.new() as client:
  balance = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
```

You can also pass the key directly, instead of relying on the environment:

```python
from typed_etherscan import Etherscan

async with Etherscan.new(api_key='your_api_key') as client:
  balance = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
```

## Rate Limiting

Etherscan's free tier enforces a strict per-second call cap. Set `ETHERSCAN_RATE_LIMIT` (or
pass `rate_limit=` to `Etherscan.new`) to cap calls client-side and avoid `RateLimited`
errors; leave it unset and Etherscan's own cap is the only limit, enforced reactively after
you've already gone over it.

```python
from typed_etherscan import Etherscan

async with Etherscan.new(rate_limit=4) as client:
  usage = await client.usage.api_limit()  # check your current usage
```

## Public Access

One endpoint needs no key at all: the list of chains the V2 API supports.

```python
from typed_etherscan import Etherscan

async with Etherscan.new(public=True) as client:
  chains = await client.usage.chain_list()
```

Every other endpoint raises `AuthError` on a client built with `public=True`.
