# Chains & Units

Gate DEX identifies chains by numeric id, tokens by contract address, and states amounts in
two different units depending on the call. The client keeps Gate's wire types, so the type
checker tells you which form each method takes.

## Chain Ids

`client.trade.chains()` returns the chains swaps route on. In October 2026 they were:

| Chain | Id | Chain | Id |
| --- | --- | --- | --- |
| Ethereum | `1` | Avalanche C | `43114` |
| BNB Smart Chain | `56` | Merlin | `4200` |
| Arbitrum One | `42161` | zkSync Era | `324` |
| Base | `8453` | Blast | `81457` |
| Optimism | `10` | Linea | `59144` |
| Polygon | `137` | World Chain | `480` |
| Gate Layer | `10088` | Solana | `501` |
| Sui | `784` | Tron | `195` |
| TON | `607` | | |

Market data and token calls keep their own chain lists, which need not match this one. A
chain a call does not support raises `BadRequest`.

## Integer Or String

Gate takes `chain_id` as an integer on some actions and as a string on others, and rejects
the wrong one:

| Takes `chain_id` as | Methods |
| --- | --- |
| `int` (`1`) | `client.trade.dexes`, `gas_price`, `quote`, `build`, `status`, `history`; `client.market.price`, `candles`, `volume_stats`, `liquidity_events` |
| `str` (`'1'`) | `client.trade.tokens`; every `client.market.token.*` method except `ranking` |
| `{'eq': '1'}` or `{'in': ['1', '501']}` | `client.market.token.ranking` |

Responses differ the same way: `chain_id` is a string in `trade.chains()`,
`token.base_info` and `token.trade_info`, and an integer elsewhere.

## Token Addresses

- `'-'` stands for the chain's native coin in `trade.quote` and `trade.build`. Quotes report
  a native coin as its wrapped token (`WETH`, `WSOL`, `WTRX`) with `is_native_token` set to
  `1`.
- Gate asks for lowercase contract addresses on EVM chains. Wallet addresses may be
  checksummed.
- On Solana, a token is its mint address.

## Amounts

| Unit | Where |
| --- | --- |
| Human-decimal (`'0.01'` ETH) | `trade.quote`, `trade.approve_transaction` and `trade.build` amounts; `trade.tokens` balances; `token.wallet_amount`; liquidity event amounts |
| Raw smallest units (wei, lamports) | `unsigned_tx.value` from `trade.build`; every amount on an order from `trade.status` and `trade.history`; `token.top_holders` on EVM chains |

`token.top_holders` amounts are human-decimal on Solana. Divide a raw amount by
`10 ** decimals` of its token (`token_in_decimals`/`token_out_decimals` on an order,
`decimal` from `token.base_info`) to get the human figure.

Prices, market caps and liquidity are in USD, and so are the `volume_*` fields, candle `vU`
and `total_volume_usd`. As of October 2026, Gate does not state the units of
`market.volume_stats`: its Chinese docs suggest `buyVolume`/`sellVolume` are token quantities
and `buyAmount`/`sellAmount` USD values.

Numbers keep the form Gate sends them in. Most decimal strings (quote, build and candle
figures, `market.price`, `trade.tokens` and `token.wallet_amount` balances) arrive as
`Decimal`. JSON numbers arrive as `float`: `token.trade_info`, the market data beside a
`token.wallet_amount` balance, liquidity events, new tokens, rankings and volume statistics.
A few numeral strings stay `str`: order amounts from `trade.status` and `trade.history`,
`unsigned_tx.value`, and the taxes and percentages in `token.risk`.
