# Typed Gate DEX

> A fully typed, validated async client for the Gate DEX API.

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
see [API Keys Setup](api-keys.md).

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

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Research Tokens](how-to/research-tokens.md)
- [Swap Tokens](how-to/swap-tokens.md)
- [Paginate Through Results](how-to/paginate-through-results.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Chains & Units](reference/chains-and-units.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Gate DEX follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
