# Getting Started

This guide gets you from installation to your first public and authenticated Bit2Me requests.

## Install The Package

```bash
pip install typed-bit2me
```

## Make A Public Request

For public-only market data, use `Bit2Me.public()`:

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  tickers = await client.v2.trading.tickers(symbol='BTC/EUR')
  print(tickers[0]['close'])
```

## Make An Authenticated Request

Once your credentials are configured, you can call private endpoints:

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  print(balances[0]['balance'])
```

## Context Manager Pattern

Use `async with` so HTTP sessions open and close cleanly:

```python
async with Bit2Me.new() as client:
  ...
```

See [Reference > Async Usage](reference/async-usage.md) for the recommended lifecycle pattern.

## Next Steps

- Go to [API Keys Setup](api-keys.md) if you have not configured credentials yet
- Read [API Overview](api-overview.md) to understand the versioned router structure
- Browse [How To](how-to/index.md) for common workflows
