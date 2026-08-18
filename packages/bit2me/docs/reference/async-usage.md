# Async Usage

You can either:

- construct the client directly for quick one-off usage
- use `async with` when you want explicit lifecycle management

## Authenticated Router

The main authenticated entry point is `Bit2Me.new()`.

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
```

This is the recommended default style for authenticated workflows.

## Public-Only Routers

For public-only usage, construct `Bit2Me.public()`.

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  tickers = await client.v2.trading.tickers(symbol='BTC/EUR')
```

## Direct Construction

Plain construction also works for quick one-off flows:

```python
from bit2me import Bit2Me

client = Bit2Me.new()
balances = await client.v1.trading.balance()
```

Use `async with` when:

- you are doing multiple requests in the same flow
- you want predictable cleanup
- you are sharing one HTTP client across several endpoint objects
