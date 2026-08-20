# Look Up Token Prices

Use `client.prices` for Alchemy Prices API methods. These methods are global
and do not take a network selector.

## Current Prices By Symbol

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  prices = await client.prices.by_symbol(symbols=['ETH', 'BTC'])
  print(prices['data'])
```

## Current Prices By Contract

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  prices = await client.prices.by_address({
    'addresses': [
      {
        'network': 'eth-mainnet',
        'address': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
      }
    ],
  })
  print(prices['data'])
```

## Historical Prices

`startTime`/`endTime` are real `datetime` values — Alchemy's wire format (Unix seconds) is
handled for you:

```python
from datetime import datetime, timedelta, timezone
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  end = datetime.now(timezone.utc)
  start = end - timedelta(days=7)
  history = await client.prices.historical({
    'symbol': 'ETH',
    'startTime': start,
    'endTime': end,
    'interval': '1d',
  })
  print(history['data'])
```
