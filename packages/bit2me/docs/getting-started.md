# Getting Started

## Install The Package

```bash
pip install typed-bit2me python-dotenv
```

## Public Requests

Public endpoints (market data, tickers, order books) need no credentials, so use `Bit2Me.public()`:

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  book = await client.v2.trading.order_book(symbol='BTC/EUR')
  print(book.get('bids', [])[:1])
```

## Authenticated Requests

Create an API key/secret pair from your Bit2Me account's API key management page:

<https://account.bit2me.com/api-keys>

Store them in a `.env` file:

```bash
# .env
BIT2ME_API_KEY="your_api_key"
BIT2ME_SECRET_KEY="your_secret_key"
```

`Bit2Me.new()` reads `BIT2ME_API_KEY`/`BIT2ME_SECRET_KEY` from the environment when no explicit `api_key`/`api_secret` is passed:

```python
from dotenv import load_dotenv
from bit2me import Bit2Me

load_dotenv()

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  print(balances[0].get('currency'), balances[0].get('balance'))
```

Passing credentials directly works too, and overrides the environment:

```python
from bit2me import Bit2Me

async with Bit2Me.new(api_key='your_api_key', api_secret='your_secret_key') as client:
  ...
```

## Client Surface

`Bit2Me.new()`/`.public()` give you three peer HTTP routers plus both WebSocket surfaces:

- `client.v1`, `client.v2`, `client.v3`: the REST surface, split exactly as Bit2Me's own API versions (trading, wallet, account, earn, and more live under `v1`; newer market-data and account routes under `v2`/`v3`)
- `client.trading_ws`: the Trading Spot WebSocket (public/private channel subscriptions and order commands)
- `client.crypto_ws`: the account-notifications WebSocket

Each one connects lazily on first use, so you don't need to open anything explicitly. `Bit2Me`'s own `async with` only covers `client.http`; wrap `client.trading_ws`/`client.crypto_ws` in their own `async with` too if you want deterministic cleanup.

See [How To](how-to/index.md) for task-focused guides across all of these.

## Next Steps

- Browse [How To](how-to/index.md) for market data, streams, orders, account data, earn, and funds workflows
- Read [Error Handling](reference/error-handling.md) for the exception hierarchy
