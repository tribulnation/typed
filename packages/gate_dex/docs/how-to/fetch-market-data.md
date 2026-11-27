# Fetch Market Data

`client.market` serves on-chain prices, candles, trading volume and liquidity events for any
token Gate DEX tracks. Tokens are identified by chain id and contract address (lowercase on
EVM chains, the mint address on Solana); see [Chains & Units](../reference/chains-and-units.md).

## Price

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  price = await client.market.price(
    chain_id=1, token_address='0xdac17f958d2ee523a2206206994597c13d831ec7'
  )
  print(price['price'], price['time'])  # Decimal USD price, datetime
```

## Candles

```python
from datetime import datetime, timezone
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  candles = await client.market.candles(
    chain_id=1,
    token_address='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',  # WETH
    period=3600,  # one hour
    end=datetime(2026, 10, 17, tzinfo=timezone.utc),
    limit=24,
  )
  for candle in candles:
    print(candle['ts'], candle['o'], candle['h'], candle['l'], candle['c'], candle['vU'])
```

`period` is the interval in seconds, from `1` up to `2592000` (30 days); the type lists every
accepted value. Prices and the `vU` volume are in USD.

Candles come newest first. `start` and `end` are both inclusive; when the range holds more
than `limit` candles, Gate returns the newest ones. `limit` defaults to 100; a `limit` above
300 is rejected with code `21003`, raised as `BadRequest`. Gate keeps only the latest 1440
candles per token and period, so a range reaching further back comes back short.
`candles_paged` walks a range wider than one page, given a `limit` of at least 2 (see
[Paginate Through Results](paginate-through-results.md)).

## Trading Volume

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  stats = await client.market.volume_stats(
    chain_id=1, token_address='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
  )
  day = stats['24h']  # also '5m', '1h' and '4h'
  print(day['buyAmount'], day['sellAmount'], day['txCountBuy'], day['txCountSell'])
```

Pass `pair_address` to count only one pool's trades. Gate does not state the units: its
Chinese docs suggest `buyVolume`/`sellVolume` are token quantities and
`buyAmount`/`sellAmount` USD values.

As of October 2026, Gate answers with zeros in every window, and a `timestamp` of `0`, even
for heavily traded tokens such as WETH and USDT on Ethereum, so a zero here does not mean the
token did not trade. `client.market.token.trade_info` reports trading volume in USD (see
[Research Tokens](research-tokens.md)).

## Liquidity Events

Liquidity adds and removes across a token's pools, newest first, up to 15 per page:

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  page = await client.market.liquidity_events(
    chain_id=1,
    token_address='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    page_index=1,
    page_size=15,
  )
  print(page['page']['total'])  # events across every page
  for event in page['data']:
    print(event['block_timestamp'], event['side'], event['dex'], event['total_volume_usd'])
```

Token amounts on an event (`amount0`, `amount1`) are human-decimal. Pass `pair_address` to
list one pool only, and use `liquidity_events_paged` to walk every page.

## Gas Prices

Current gas estimates for a chain live under `client.trade`, next to the swap calls that use
them; see [Swap Tokens](swap-tokens.md#gas-prices).
