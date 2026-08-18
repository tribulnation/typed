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

## Documentation

- [API Keys Setup](https://tribulnation.com/typed/kraken/api-keys)
- [How To](https://tribulnation.com/typed/kraken/how-to)
- [Reference](https://tribulnation.com/typed/kraken/reference)

## How To

- [Fetch Market Data](https://tribulnation.com/typed/kraken/how-to/fetch-market-data)
- [Listen To Streams](https://tribulnation.com/typed/kraken/how-to/listen-to-streams)
- [Place & Manage Orders](https://tribulnation.com/typed/kraken/how-to/place-and-manage-orders)
- [Fetch Account Data](https://tribulnation.com/typed/kraken/how-to/fetch-account-data)
- [Query & Manage Earn Instruments](https://tribulnation.com/typed/kraken/how-to/query-and-manage-earn)
- [Deposits & Withdrawals](https://tribulnation.com/typed/kraken/how-to/deposits-and-withdrawals)

## Source Code

> [github.com/tribulnation/kraken](https://github.com/tribulnation/kraken)
