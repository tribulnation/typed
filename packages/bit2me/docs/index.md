# Typed Bit2Me

> A fully typed, validated async client for the Bit2Me API.

```python
from dotenv import load_dotenv
from typed_bit2me import Bit2Me

load_dotenv()

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  print(balances[0].get('currency'), balances[0].get('balance'))
```

## Why Typed Bit2Me?

- **🎯 Precise Types**: literal types for order sides, order types, and statuses; `Decimal` for prices and amounts; a full `TypedDict` per response.
- **✅ Runtime Validation**: every REST response and every WebSocket push is validated against its documented schema by default.
- **⚡ Async First**: async HTTP plus two independent WebSocket surfaces (the Trading Spot socket for order commands and channel subscriptions, and the account-notifications socket), built for concurrent trading workflows.
- **📚 Full Surface**: the complete `v1`/`v2`/`v3` REST surface (trading, wallet, account, earn, and more), not just tickers.

## Installation

```bash
pip install typed-bit2me
```

## Quick Start

### Public market data

`Bit2Me.new(public=True)` needs no credentials and reaches every public endpoint.

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new(public=True) as client:
  book = await client.v2.trading.order_book(symbol='BTC/EUR')
  print(book.get('bids', [])[:1])
```

### Authenticated client

```bash
# .env
BIT2ME_API_KEY="your_api_key"
BIT2ME_SECRET_KEY="your_secret_key"
```

```python
from dotenv import load_dotenv
from typed_bit2me import Bit2Me

load_dotenv()

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  print(balances[0].get('currency'), balances[0].get('balance'))
```

## Client Surface

- `client.v1`, `client.v2`, `client.v3`: the Bit2Me HTTP surface (Crypto API, Embed API, Trading Spot REST), organized exactly as Bit2Me's own API versions.
- `client.trading_ws`: the Trading Spot WebSocket, public/private channel subscriptions and the six one-shot order commands, on one connection.
- `client.crypto_ws`: the account-notifications WebSocket, one authenticated connection, every entitled notification pushed unprompted.

Response validation is on by default; pass `validate=False` to `Bit2Me.new()`, or per call, to skip it.

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Query & Manage Earn](how-to/manage-earn.md)
- [Query & Manage Deposits/Withdrawals](how-to/manage-deposits-and-withdrawals.md)

## Reference

- [Getting Started](getting-started.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Bit2Me follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
