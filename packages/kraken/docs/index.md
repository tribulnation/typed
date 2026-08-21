# Typed Kraken

> A fully typed, validated async client for the Kraken Spot API -- REST and WebSocket v2.

```python
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  ticker = await client.spot.market_data.ticker(pair='XBTUSD')
  print(ticker)
```

## Why Typed Kraken?

- **🎯 Precise Types**: every `client.spot`, `client.streams`, and `client.trading_ws`
  parameter and response is typed, down to `TypedDict`s and `Literal`s for Kraken's own
  field names.
- **✅ Runtime Validation**: REST and WebSocket v2 responses are validated against their
  schema before you see them, not just typed on paper.
- **⚡ Async First**: async REST calls and long-lived WebSocket v2 subscriptions, built for
  concurrent trading workflows.
- **📚 Full Surface**: market data, account, trading, funding, and earn -- every documented
  Kraken Spot endpoint, not just the popular ones.

## Installation

```bash
pip install typed-kraken
```

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Query & Manage Earn Instruments](how-to/query-and-manage-earn.md)
- [Deposits & Withdrawals](how-to/deposits-and-withdrawals.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Kraken follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
