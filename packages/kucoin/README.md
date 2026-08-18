# Typed KuCoin

> A fully typed, validated async client for the KuCoin API.

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  ticker = await client.spot.ticker(symbol='BTC-USDT')
  print(ticker['price'])
```

## Why Typed KuCoin?

- **🎯 Precise Types**: every request and response across Spot, Margin, Futures and Earn is
  a typed structure, not a bare `dict`.
- **✅ Runtime Validation**: responses are checked against their schema by default, not just
  typed on paper.
- **⚡ Async First**: one client shares an HTTP connection pool per KuCoin host and lazily
  opens spot/margin and futures WebSocket streams only when used.
- **📚 Full Surface**: Account, Spot, Margin, Futures, Earn, VIP Lending, Affiliate, Convert,
  Copy Trading and Broker each hang off their own attribute on `KuCoin`, alongside both
  public and private WebSocket feeds.

## Installation

```bash
pip install typed-kucoin
```

## Documentation

- [API Keys Setup](https://tribulnation.com/typed/kucoin/api-keys)
- [How To](https://tribulnation.com/typed/kucoin/how-to)
- [Reference](https://tribulnation.com/typed/kucoin/reference)

## How To

- [Fetch Market Data](https://tribulnation.com/typed/kucoin/how-to/fetch-market-data)
- [Listen To Streams](https://tribulnation.com/typed/kucoin/how-to/listen-to-streams)
- [Place & Manage Orders](https://tribulnation.com/typed/kucoin/how-to/place-and-manage-orders)
- [Manage Account Data](https://tribulnation.com/typed/kucoin/how-to/manage-account-data)
- [Query & Manage Earn Instruments](https://tribulnation.com/typed/kucoin/how-to/manage-earn)
- [Deposits & Withdrawals](https://tribulnation.com/typed/kucoin/how-to/manage-deposits-and-withdrawals)
- [Paginate Through Results](https://tribulnation.com/typed/kucoin/how-to/paginate-through-results)

## Source Code

> [github.com/tribulnation/kucoin](https://github.com/tribulnation/kucoin)
