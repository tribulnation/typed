# Typed Clients

Async, typed, validated Python clients for every crypto venue we trade on. One namespace. Every exchange.

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.market.ticker_price(symbol='BTCUSDT')
  print(price)
```

## Why typed?

- **🎯 Precise Types**: Typed endpoint inputs and responses, not `dict`/`Any`.
- **✅ Runtime Validation**: Responses validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP and streaming, built for concurrent workflows.
- **📚 Full Surface**: Every documented endpoint, not just the popular ones.

## Packages

Every client builds on [`typed-core`](packages/core).

| | Repo | Status | PyPI |
|--|------|--------|-----|
| <img src="https://catalogue.tribulnation.com/icons/platform/binance.svg" width="20" height="20" /> | [Binance](https://github.com/tribulnation/typed/tree/main/packages/binance) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-binance)](https://pypi.org/project/typed-binance/) |
| <img src="https://catalogue.tribulnation.com/icons/platform/coinbase.svg" width="20" height="20" /> | [Coinbase](https://github.com/tribulnation/typed/tree/main/packages/coinbase) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-coinbase)](https://pypi.org/project/typed-coinbase/) |
| <img src="https://catalogue.tribulnation.com/icons/platform/bybit.svg" width="20" height="20" /> | [Bybit](https://github.com/tribulnation/typed/tree/main/packages/bybit) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-bybit)](https://pypi.org/project/typed-bybit/) |
| <img src="https://catalogue.tribulnation.com/icons/asset/bitget-token.svg" width="20" height="20" /> | [Bitget](https://github.com/tribulnation/typed/tree/main/packages/bitget) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-bitget)](https://pypi.org/project/typed-bitget/) |
| <img src="https://catalogue.tribulnation.com/icons/asset/hyperliquid.svg" width="20" height="20" /> | [Hyperliquid](https://github.com/tribulnation/typed/tree/main/packages/hyperliquid) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-hyperliquid)](https://pypi.org/project/typed-hyperliquid/) |
| <img src="https://catalogue.tribulnation.com/icons/platform/mexc.svg" width="20" height="20" /> | [MEXC](https://github.com/tribulnation/typed/tree/main/packages/mexc) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-mexc)](https://pypi.org/project/typed-mexc/) |
| <img src="https://catalogue.tribulnation.com/icons/platform/kucoin.svg" width="20" height="20" /> | [KuCoin](https://github.com/tribulnation/typed/tree/main/packages/kucoin) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-kucoin)](https://pypi.org/project/typed-kucoin/) |
| <img src="https://catalogue.tribulnation.com/icons/platform/kraken.svg" width="20" height="20" /> | [Kraken](https://github.com/tribulnation/typed/tree/main/packages/kraken) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-kraken)](https://pypi.org/project/typed-kraken/) |
| <img src="https://catalogue.tribulnation.com/icons/asset/dydx.svg" width="20" height="20" /> | [dYdX](https://github.com/tribulnation/typed/tree/main/packages/dydx) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-dydx)](https://pypi.org/project/typed-dydx/) |
| <img src="https://catalogue.tribulnation.com/icons/platform/deribit.svg" width="20" height="20" /> | [Deribit](https://github.com/tribulnation/typed/tree/main/packages/deribit) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-deribit)](https://pypi.org/project/typed-deribit/) |
| <img src="https://catalogue.tribulnation.com/icons/asset/bit2me.svg" width="20" height="20" /> | [Bit2Me](https://github.com/tribulnation/typed/tree/main/packages/bit2me) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-bit2me)](https://pypi.org/project/typed-bit2me/) |
| <img src="https://catalogue.tribulnation.com/icons/platform/alchemy.svg" width="20" height="20" /> | [Alchemy](https://github.com/tribulnation/typed/tree/main/packages/alchemy) | ✅ Production | [![PyPI](https://img.shields.io/pypi/v/typed-alchemy)](https://pypi.org/project/typed-alchemy/) |
| <img src="https://catalogue.tribulnation.com/icons/platform/moralis.svg" width="20" height="20" /> | [Moralis](https://github.com/tribulnation/typed/tree/main/packages/moralis) | 🔧 In development | [![PyPI](https://img.shields.io/pypi/v/typed-moralis)](https://pypi.org/project/typed-moralis/) |
| <img src="https://catalogue.tribulnation.com/icons/platform/etherscan.svg" width="20" height="20" /> | [Etherscan](https://github.com/tribulnation/typed/tree/main/packages/etherscan) | 🔧 In development | [![PyPI](https://img.shields.io/pypi/v/typed-etherscan)](https://pypi.org/project/typed-etherscan/) |

More venues are on the way — see the [full catalog](https://tribulnation.com/typed).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md): most of the source code is generated from an internal spec. So, open issues not PRs please! If you want to collaborate further, please reach out to us at marcel@tribulnation.com :)

## License

MIT — see [LICENSE](LICENSE).
