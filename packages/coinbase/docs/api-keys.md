# API Keys Setup

Typed Coinbase authenticates with a **CDP API Key** — one keypair that signs a short-lived JWT per request. It is not classic HMAC key/secret signing and not an OAuth2 flow.

## Create a Key

Create a CDP API Key from your account's [API settings](https://www.coinbase.com/settings/api):

| 1) Create API keys                                  | 2) Copy API & Secret key |
| --------------------------------------------------- | --------------------------------------------------- |
|![How to create API keys](media/create_api_keys.png) | ![How to copy API keys](media/copy_api_keys.png) |

## Environment Variables

```bash
export COINBASE_API_KEY_NAME="organizations/{org_id}/apiKeys/{key_id}"
export COINBASE_PRIVATE_KEY="-----BEGIN EC PRIVATE KEY-----..."
```

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  accounts = await client.advanced_trade.accounts.list()
```

## Direct Usage

```python
from typed_coinbase import Coinbase

async with Coinbase.new(
  key_name='organizations/{org_id}/apiKeys/{key_id}',
  private_key='-----BEGIN EC PRIVATE KEY-----...',
) as client:
  ...
```

## Public-Only Usage

The product catalog under `advanced_trade.products.public`, and the `market_data` WebSocket channels, need no key at all. Skip credential resolution entirely with `public=True`:

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  product = await client.advanced_trade.products.public.get('BTC-USD')
```

See [Environment Variables](reference/env-vars.md) for the full variable list, and [Error Handling](reference/error-handling.md) for what an authenticated call raises without credentials.
