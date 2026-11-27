# Typed

Async, typed and validated Python clients for crypto exchanges and on-chain data APIs.

[![License: MIT](https://img.shields.io/github/license/tribulnation/typed)](LICENSE)
[![Check](https://github.com/tribulnation/typed/actions/workflows/check.yml/badge.svg)](https://github.com/tribulnation/typed/actions/workflows/check.yml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)](https://pypi.org/project/typed-hyperliquid/)

## Why

- Request parameters and responses are `TypedDict`s, so your editor and type checker know the shape of every call.
- Responses are validated and parsed at runtime by default: prices the venue sends as strings arrive as `Decimal`. Pass `validate=False` to get the raw JSON values instead.
- Async throughout: HTTP calls and WebSocket streams.
- Each exchange client covers the venue's documented endpoints, trading and account ones included. The code is generated from a spec of each venue's API.

## Install

There is one package per venue. Install the ones you need:

```bash
pip install typed-hyperliquid
```

Python 3.10 or newer. The clients share `typed-core`, which is installed with them.

## Quickstart

Fetch the best bid and ask for BTC on Hyperliquid. Public endpoints need no API key.

```python
import asyncio
from typed_hyperliquid import Hyperliquid

async def main():
  async with Hyperliquid.new(public=True) as client:
    book = await client.info.l2_book('BTC')
    bids, asks = book['levels']
    print(bids[0], asks[0])

asyncio.run(main())
```

```
{'n': 5, 'px': Decimal('60027.0'), 'sz': Decimal('0.11931')} {'n': 15, 'px': Decimal('60028.0'), 'sz': Decimal('4.08393')}
```

The exchange clients work the same way: `<Venue>.new(...)`, then `async with`. Pass credentials to `new()` for private endpoints. Each package's docs show how.

## Packages

| Venue | PyPI package | Status | Docs |
|---|---|---|---|
| Binance | [`typed-binance`](https://pypi.org/project/typed-binance/) | Production | [docs](https://tribulnation.com/typed/binance) |
| Coinbase | [`typed-coinbase`](https://pypi.org/project/typed-coinbase/) | Beta | [docs](https://tribulnation.com/typed/coinbase) |
| Bybit | [`typed-bybit`](https://pypi.org/project/typed-bybit/) | Beta | [docs](https://tribulnation.com/typed/bybit) |
| Bitget | [`typed-bitget`](https://pypi.org/project/typed-bitget/) | Beta | [docs](https://tribulnation.com/typed/bitget) |
| Hyperliquid | [`typed-hyperliquid`](https://pypi.org/project/typed-hyperliquid/) | Production | [docs](https://tribulnation.com/typed/hyperliquid) |
| MEXC | [`typed-mexc`](https://pypi.org/project/typed-mexc/) | Production | [docs](https://tribulnation.com/typed/mexc) |
| KuCoin | [`typed-kucoin`](https://pypi.org/project/typed-kucoin/) | Beta | [docs](https://tribulnation.com/typed/kucoin) |
| Kraken | [`typed-kraken`](https://pypi.org/project/typed-kraken/) | Beta | [docs](https://tribulnation.com/typed/kraken) |
| dYdX | [`typed-dydx`](https://pypi.org/project/typed-dydx/) | Production | [docs](https://tribulnation.com/typed/dydx) |
| Deribit | [`typed-deribit`](https://pypi.org/project/typed-deribit/) | Beta | [docs](https://tribulnation.com/typed/deribit) |
| Aster | [`typed-aster`](https://pypi.org/project/typed-aster/) | Beta | [docs](https://tribulnation.com/typed/aster) |
| Lighter | [`typed-lighter`](https://pypi.org/project/typed-lighter/) | Beta | [docs](https://tribulnation.com/typed/lighter) |
| GRVT | [`typed-grvt`](https://pypi.org/project/typed-grvt/) | Beta | [docs](https://tribulnation.com/typed/grvt) |
| Extended | [`typed-extended`](https://pypi.org/project/typed-extended/) | Beta | [docs](https://tribulnation.com/typed/extended) |
| Bit2Me | [`typed-bit2me`](https://pypi.org/project/typed-bit2me/) | Beta | [docs](https://tribulnation.com/typed/bit2me) |
| Margin Trade | [`typed-margin-trade`](https://pypi.org/project/typed-margin-trade/) | Beta | [docs](https://tribulnation.com/typed/margin_trade) |
| gTrade | [`typed-gtrade`](https://pypi.org/project/typed-gtrade/) | Beta | [docs](https://tribulnation.com/typed/gtrade) |
| Nado | [`typed-nado`](https://pypi.org/project/typed-nado/) | Beta | [docs](https://tribulnation.com/typed/nado) |
| RISEx | [`typed-risex`](https://pypi.org/project/typed-risex/) | Beta | [docs](https://tribulnation.com/typed/risex) |
| EVEDEX | [`typed-evedex`](https://pypi.org/project/typed-evedex/) | Beta | [docs](https://tribulnation.com/typed/evedex) |
| Alchemy | [`typed-alchemy`](https://pypi.org/project/typed-alchemy/) | Production | [docs](https://tribulnation.com/typed/alchemy) |
| Moralis | [`typed-moralis`](https://pypi.org/project/typed-moralis/) | Beta | [docs](https://tribulnation.com/typed/moralis) |
| Etherscan | [`typed-etherscan`](https://pypi.org/project/typed-etherscan/) | Beta | [docs](https://tribulnation.com/typed/etherscan) |
| Ethereum nodes (Web3.py) | [`typed-ethereum`](https://pypi.org/project/typed-ethereum/) | Beta | [README](https://github.com/tribulnation/typed/tree/main/packages/ethereum) |
| Shared core (installed with the clients) | [`typed-core`](https://pypi.org/project/typed-core/) | - | [README](https://github.com/tribulnation/typed/tree/main/packages/core) |

Documentation for every client: [tribulnation.com/typed](https://tribulnation.com/typed).

## Status

Production packages are used in live trading. Beta packages work but their API may still change. Each package is versioned and released on its own, tagged `<package>-vX.Y.Z`.

## Contributing

The code is generated from a spec kept outside this repo, so a PR here would be overwritten. Please [open an issue](https://github.com/tribulnation/typed/issues) instead; see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE).
