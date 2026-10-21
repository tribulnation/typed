# Typed Margin Trade

<p align="center">
  <em>A fully typed, validated async client for the Margin Trade API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-margin_trade/">
    <img src="https://img.shields.io/pypi/v/typed-margin_trade.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-margin_trade/">
    <img src="https://img.shields.io/pypi/pyversions/typed-margin_trade.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/margin_trade">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-margin_trade.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/margin_trade](https://tribulnation.com/typed/margin_trade)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/margin_trade](https://github.com/tribulnation/typed/tree/main/packages/margin_trade)

---

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
[Authenticated Setup](https://tribulnation.com/typed/margin_trade/authenticated-setup).

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True, mainnet=False) as client:
  mids = await client.info.all_mids()  # testnet prices
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/margin_trade/how-to/fetch-market-data)
- [Fetch Account Data](https://tribulnation.com/typed/margin_trade/how-to/fetch-account-data)
- [Place & Manage Orders](https://tribulnation.com/typed/margin_trade/how-to/place-and-manage-orders)
- [Paginate Through Results](https://tribulnation.com/typed/margin_trade/how-to/paginate-through-results)
- [Listen To Live Streams](https://tribulnation.com/typed/margin_trade/how-to/listen-to-live-streams)
- [Manage Deposits & Withdrawals](https://tribulnation.com/typed/margin_trade/how-to/manage-deposits-withdrawals)

## Reference

- [Authenticated Setup](https://tribulnation.com/typed/margin_trade/authenticated-setup)
- [Async Usage](https://tribulnation.com/typed/margin_trade/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/margin_trade/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/margin_trade/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/margin_trade/reference/timestamps)

## License

MIT — see [LICENSE](LICENSE).
