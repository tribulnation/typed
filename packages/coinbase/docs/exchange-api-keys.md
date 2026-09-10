# Exchange API Keys Setup

Coinbase Exchange (formerly Pro/GDAX) is a separate, institutional product from Coinbase App — it authenticates with its own key/secret/passphrase, signed per-request with HMAC-SHA256. This is a wholly different credential from the CDP API Key `client.app` uses; see [API Keys Setup](api-keys.md) for that one.

## Create a Key

Exchange access is institutional. Create a key — key, secret, and passphrase, shown once — from your Exchange account's [API settings](https://exchange.coinbase.com/profile/api). See the [authentication docs](https://docs.cdp.coinbase.com/exchange/rest-api/authentication) for how each value is used to sign a request.

## Environment Variables

```bash
export COINBASE_EXCHANGE_API_KEY="..."
export COINBASE_EXCHANGE_API_SECRET="..."
export COINBASE_EXCHANGE_PASSPHRASE="..."
```

```python
from typed_coinbase import Coinbase

async with Coinbase.new(exchange_public=False) as client:
  accounts = await client.exchange.http.accounts.list()
```

## Direct Usage

```python
from typed_coinbase import Coinbase

async with Coinbase.new(
  exchange_public=False,
  exchange_key='...',
  exchange_secret='...',
  exchange_passphrase='...',
) as client:
  ...
```

## Public-Only Usage (the default)

`exchange_public` defaults to `True` — a plain `Coinbase.new()` already builds a public-only `exchange`, no Exchange credentials needed at all:

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  products = await client.exchange.http.products.list()
```

That reaches `exchange.http.products`/`exchange.http.currencies` and the public WebSocket Feed channels (`heartbeat`, `status`, `ticker`, `ticker_batch`, `level2_batch`, `matches`, `rfq_matches`, `auction`). Set `exchange_public=False` and supply the three values above to reach the private surface instead — accounts, orders, fills, transfers, and the private WebSocket channels (`full`, `user`, `level2`, `level3`, `balance`), e.g.:

```python
from typed_coinbase import Coinbase

async with Coinbase.new(exchange_public=False) as client:
  open_orders = await client.exchange.http.orders.list(limit=50, status=['open'])
  async with client.exchange.streams.user(product_ids=['BTC-USD']) as order_events:
    async for message in order_events:
      ...
```

See [Environment Variables](reference/env-vars.md) for the full variable list, and [Error Handling](reference/error-handling.md) for what an authenticated call raises without credentials.
