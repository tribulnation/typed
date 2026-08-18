# Typed Bit2Me

> Fully typed, validated async routers for the Bit2Me REST APIs.

**Use autocomplete instead of documentation.**

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  print(balances[0]['currency'])
```

## Why Typed Bit2Me?

- **🎯 Precise Types**: Literal types where they help, so your IDE knows what is valid.
- **✅ Automatic Validation**: Catch upstream API changes earlier.
- **⚡ Async First**: Built for concurrent, network-heavy workflows.
- **🔒 Type Safety**: Full type hints throughout.
- **🎨 Better DX**: Clear versioned routing and explicit public vs authenticated access.
- **📦 Pragmatic Surface**: Public market-data endpoints, signed authenticated requests, and direct access to versioned API groups.

## Installation

```bash
pip install typed-bit2me
```

## Quick Start

### Public market data

For public-only market data, use `Bit2Me.public()`.

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  tickers = await client.v2.trading.tickers(symbol='BTC/EUR')
  print(tickers[0]['close'])
```

### Authenticated router

Set up credentials first:

```bash
export BIT2ME_API_KEY="your_api_key"
export BIT2ME_SECRET_KEY="your_secret_key"
```

Then use the authenticated versioned router:

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  print(balances[0]['balance'])
```

## Features

### Versioned Routing

The package mirrors the Bit2Me REST API versions explicitly:

- `Bit2Me.v1`
- `Bit2Me.v2`
- `Bit2Me.v3`

### Automatic Validation

Response validation is **on by default** but can be disabled:

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()

async with Bit2Me.new(validate=False) as client:
  raw_balances = await client.v1.trading.balance()
```

## API Coverage

Current coverage is organized around the versioned Bit2Me APIs:

- `Bit2Me.v1` for trading, wallet, account, earn, teller, signin, and related operational endpoints
- `Bit2Me.v2` for trading, wallet, currency, earn, loan, and account routes
- `Bit2Me.v3` for newer account, currency, and signin routes

Public market-data calls can be made through `Bit2Me.public()`.

WebSocket support is not implemented in the current package.

📋 See [API Overview](api-overview.md) for the current coverage and structure.

## Documentation

- [**Getting Started**](getting-started.md) - Install the package and make your first requests
- [**API Keys Setup**](api-keys.md) - Configure credentials for authenticated router usage
- [**API Overview**](api-overview.md) - Understand the client structure and coverage
- [**How To**](how-to/index.md) - Task-focused guides for market data, orders, balances, wallet flows, and earn data
- [**Reference**](reference/index.md) - Async usage, error handling, env vars, and API reference

## Design Philosophy

Typed Bit2Me follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
