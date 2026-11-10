# Query Protocol Data

Two public surfaces expose gTrade's protocol state and history, no credentials needed:

- `client.backend`: the chain's trading backend, a cache of on-chain state.
- `client.backend_global`: stats, trading history, leaderboards, contests and referrals
  across chains. Its stats, trading-history and trader reads take an explicit `chain_id`
  (`42161` Arbitrum, `8453` Base, `137` Polygon); contests, referrals and
  `stats.total_supply` take none.

## Trading Variables

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  keys = await client.backend.trading_variables.keys()
  subset = await client.backend.trading_variables.by_keys(['pairs', 'fees', 'tradingState'])
  pairs = subset.get('pairs', [])
  print(subset.get('tradingState'), pairs[0]['from'], pairs[0]['to'], pairs[0]['spreadP'] / 1e10)
```

Trading variables hold every pair, group, fee tier, collateral and risk parameter. The full
payload (`trading_variables.all()`) is about 3 MB, so prefer `by_keys` for what you need.
`pairs` is append-only and indexed by `pairIndex`.

Backend values are raw contract-precision integers, not normalized: prices carry 1e10,
leverage 1e3, collateral the token's decimals. Each field's docstring states its precision;
see [Numbers & Precision](../reference/numbers.md).

## Open Trades

```python
from decimal import Decimal
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  for container in await client.backend.trades.by_trader('0x...'):
    trade = container['trade']
    print(trade['pairIndex'], trade['long'], Decimal(trade['openPrice']) / 10**10, Decimal(trade['leverage']) / 10**3)
```

`backend.trades.open()` returns every open trade and resting order on the chain;
`backend.trading_variables.user(address)` returns one trader's pending market orders,
fee tier, and collateral balances and allowances.

## Protocol Stats

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  stats = await client.backend_global.stats.chain(42161)
  apr = await client.backend_global.stats.apr(42161)
  supply = await client.backend_global.stats.total_supply()
  latest = stats['stats'][0]  # newest first
  print(latest['date'], latest['leveraged_volume'], apr['sssApr'], supply['value'])
```

`stats.holding_rates(collateral_index=..., pair_index=..., chain_id=...)` returns a market's
hourly borrowing and funding rate history.

## Trading History

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  totals = await client.backend_global.trading_history.stats('24h', chain_id=42161)
  trades = await client.backend_global.trading_history.trades('24h', chain_id=42161)
  print(totals['totalVolume'], totals['totalTrades'], trades[0]['pair'], trades[0]['date'])
```

Windows are `24h`, `48h` and `72h`. A full window holds thousands of rows (several MB).

## Leaderboards

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  weekly = await client.backend_global.traders.leaderboard(period=7, chain_id=42161)
  boards = await client.backend_global.traders.all_leaderboards(42161)  # every period at once
  print(weekly[0]['address'], weekly[0]['total_pnl_usd'], list(boards))
```

`period` is a number of days: `1`, `7`, `30` or `90`.

## Contests

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  contests = await client.backend_global.contests.list()
  for contest in contests:
    print(contest['id'], contest['start'], contest['end'], contest.get('name'), contest.get('gated'))
```

`name`, `gated` and the other fields gTrade's contest docs leave out can be missing, so read
them with `.get`.

`contests.get(id)`, `contests.leaderboard(id)` and `contests.trader(id=..., trader=...)`
read one contest. A gated contest answers its leaderboard reads with `AuthError`
("registration required").

## Referrals

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  config = await client.backend_global.referrals.config()
  summary = await client.backend_global.referrals.summary('0x...')
  print(config['l1RateBps'], summary['code'], summary['rewards']['lifetimeUsd'])
```

Also `referrals.rewards(address)`, `referrals.address_code(address)` (the code an address
owns), `referrals.code_owner(code)` (the address owning a code) and
`referrals.binding(address)` (the referrer an address is bound to); the last three return
`None` when there is none.

See the upstream [backend overview](https://docs.gains.trade/developer/integrators/backend)
and [Backend Global reference](https://docs.gains.trade/developer/api-reference/introduction).
