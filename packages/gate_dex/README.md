# Typed Gate DEX

<p align="center">
  <em>A fully typed, validated async client for the Gate DEX API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-gate_dex/">
    <img src="https://img.shields.io/pypi/v/typed-gate_dex.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-gate_dex/">
    <img src="https://img.shields.io/pypi/pyversions/typed-gate_dex.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/gate_dex">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-gate_dex.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/gate_dex](https://tribulnation.com/typed/gate_dex)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/gate_dex](https://github.com/tribulnation/typed/tree/main/packages/gate_dex)

---

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  quote = await client.trade.quote(
    chain_id=1,  # Ethereum
    amount_in='0.01',  # 0.01 ETH
    token_in='-',  # the chain's native coin
    token_out='0xdac17f958d2ee523a2206206994597c13d831ec7',  # USDT
    slippage=0.01,  # 1%
    slippage_type=1,
    user_wallet='0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
  )
  print(quote['amount_out'], quote['min_amount_out'])
```

Every Gate DEX call is signed, market data included, so the client always needs an API key:
see [API Keys Setup](https://tribulnation.com/typed/gate_dex/api-keys).

## Why Typed Gate DEX?

- **🎯 Precise Types**: Typed inputs and responses for every swap and market data call, including the per-chain-family gas price union and the two ways to submit a swap.
- **✅ Runtime Validation**: Responses validated by default, with timestamps as UTC `datetime`, Gate's decimal-string prices and amounts as exact `Decimal`, and its JSON numbers as `float`.
- **⚡ Async First**: Async HTTP with request signing done for you, plus resumable paginated walks over candles, liquidity events and token lists.
- **📚 Full Surface**: Swap quotes, approvals, builds, submission and order tracking across every Gate DEX chain (EVM, Solana, Sui, TON, Tron), plus prices, candles, liquidity events, token data, rankings and security audits.

## Installation

```bash
pip install typed-gate_dex
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/gate_dex/how-to/fetch-market-data)
- [Research Tokens](https://tribulnation.com/typed/gate_dex/how-to/research-tokens)
- [Swap Tokens](https://tribulnation.com/typed/gate_dex/how-to/swap-tokens)
- [Paginate Through Results](https://tribulnation.com/typed/gate_dex/how-to/paginate-through-results)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/gate_dex/api-keys)
- [Chains & Units](https://tribulnation.com/typed/gate_dex/reference/chains-and-units)
- [Async Usage](https://tribulnation.com/typed/gate_dex/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/gate_dex/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/gate_dex/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/gate_dex/reference/timestamps)

## Design Philosophy

Typed Gate DEX follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
