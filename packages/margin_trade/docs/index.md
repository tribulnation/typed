# Typed Margin Trade

> A fully typed, validated async client for the Margin Trade API.

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  book = await client.info.l2_book('BTC')
  bids, asks = book['levels'] or ([], [])  # an empty book answers `levels: []`
  if bids and asks:
    print(bids[0]['px'], asks[0]['px'])
```

## Why Typed Margin Trade?

- **🎯 Precise Types**: Typed requests and responses for every `info`, `exchange`, `user`, `solana`, `public` and CoinGecko call and WebSocket channel the client supports, not `dict`/`Any`; only a few nested lists the venue has only ever sent empty (fee tiers, order `children`) stay loosely typed.
- **✅ Runtime Validation**: Responses and stream pushes validated by default, with prices and sizes parsed to `Decimal` and timestamps to `datetime`.
- **⚡ Async First**: Async HTTP and WebSocket streaming over one shared connection each, with Ed25519 signing built in.
- **📚 Full Surface**: Market data, trading, agent wallets, transfers, withdrawals, account history, referrals and the testnet faucet, not just the popular calls.

## Installation

```bash
pip install typed-margin_trade
```

## Testnet And Mainnet

The client talks to mainnet by default. Pass `mainnet=False` for testnet: it picks the
testnet host and signs every request for testnet, so a signed request is only valid on the network you chose.
Testnet accounts can claim test USDC daily with `user.faucet_claim()`. The examples in these
docs use testnet and read the key from `MARGIN_TRADE_TESTNET_PRIVATE_KEY`; see
[Authenticated Setup](authenticated-setup.md).

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True, mainnet=False) as client:
  mids = await client.info.all_mids()  # testnet prices
```

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Listen To Live Streams](how-to/listen-to-live-streams.md)
- [Manage Deposits & Withdrawals](how-to/manage-deposits-withdrawals.md)

## Reference

- [Authenticated Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Margin Trade follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
