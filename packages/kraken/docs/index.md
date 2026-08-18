# Typed Kraken

> A fully typed, validated async client for the Kraken Spot API -- REST and WebSocket v2.

```python
from kraken import Kraken

async with Kraken.new(public=True) as client:
  ticker = await client.spot.market_data.ticker(pair='XBTUSD')
  print(ticker)
```

## Why Typed Kraken?

- **🎯 Precise Types**: every `client.spot` and `client.streams` parameter and response is
  typed, down to `TypedDict`s and `Literal`s for Kraken's own field names.
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

## Surface

`Kraken.new()` builds a client with two top-level surfaces:

- `client.spot` -- REST, under `https://api.kraken.com`. Composes `market_data`,
  `account`, `trading`, `funding`, and `earn`. Public methods work with no
  credentials; private ones sign each request.
- `client.streams` -- WebSocket v2. Composes `market_data` (public channel
  subscriptions), `private` (account channel subscriptions), and `trading`
  (order placement/cancellation over the wire). `private` and `trading` share one
  authenticated connection; `market_data` uses a separate public one.

Pass `public=True` to build a client with no credentials, usable only for
`spot.market_data` and `streams.market_data`.

## Documentation

- [API Keys Setup](api-keys.md)
- [How To](how-to/index.md)
- [Reference](reference/index.md)

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Query & Manage Earn Instruments](how-to/query-and-manage-earn.md)
- [Deposits & Withdrawals](how-to/deposits-and-withdrawals.md)

## Design Philosophy

Typed Kraken follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
