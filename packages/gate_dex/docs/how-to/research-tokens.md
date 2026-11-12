# Research Tokens

`client.market.token` covers token metadata, trading statistics, holders, wallet balances,
newly created tokens, leaderboards and security audits. These methods take `chain_id` as a
string (`'1'`, `'501'`), as Gate's token actions do (so does `client.trade.tokens`), except
`ranking`, which takes an `{'eq': ...}` or `{'in': [...]}` filter; the types enforce it. See
[Chains & Units](../reference/chains-and-units.md).

## Metadata And Trading Statistics

```python
from typed_gate_dex import GateDex

usdt = '0xdac17f958d2ee523a2206206994597c13d831ec7'
weth = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'

async with GateDex.new() as client:
  info = await client.market.token.base_info(chain_id='1', token_address=usdt)
  print(info['token_name'], info['token_symbol'], info['decimal'])

  stats = await client.market.token.trade_info(chain_id='1', token_address=[usdt, weth])
  for token in stats:
    print(
      token['token_address'],
      token['current_price'],
      token['market_cap'],
      token['liquidity'],
      token['holder_count'],
      token['volume_24h'],
      token['price_change_24h'],
    )
```

`trade_info` takes up to 100 addresses of one chain per call.

## Holders And Balances

```python
from typed_gate_dex import GateDex

usdt = '0xdac17f958d2ee523a2206206994597c13d831ec7'

async with GateDex.new() as client:
  top = await client.market.token.top_holders(chain_id='1', token_address=usdt)
  for holder in top['holders']:  # the 20 largest, biggest first
    print(holder['wallet'], holder['amount'])

  balance = await client.market.token.wallet_amount(
    chain_id='1',
    token_address=usdt,
    wallet='0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
  )
  print(balance['amount'], balance['current_price'])
```

`wallet_amount` returns a human-decimal balance. Gate reports `top_holders` amounts in raw
smallest units on EVM chains (divide by `10 ** decimal` from `base_info`) but human-decimal
on Solana.

## New Tokens

Tokens created in a time range, newest first, one cursor page at a time:

```python
from datetime import datetime, timezone
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  page = await client.market.token.created(
    start=datetime(2026, 10, 26, tzinfo=timezone.utc),
    end=datetime(2026, 10, 27, tzinfo=timezone.utc),
    chain_id='1',
    limit='50',
  )
  for token in page['tokens']:
    print(token['created_at'], token['symbol'], token['liquidity'], token['holder_count'])
  cursor = page.get('next_cursor')  # absent on the last page
```

Gate takes this `limit` as a numeral string, from `'1'` to `'100'` (default `'20'`). Pass
`cursor` to fetch the next page, or let `created_paged` follow it for you.

## Rankings

Rank tokens by any numeric field, optionally filtered to one chain (`{'eq': '56'}`) or
several (`{'in': ['1', '501']}`):

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  page = await client.market.token.ranking(
    chain_id={'eq': '56'},  # BNB Smart Chain
    sort=[{'field': 'trend_info.volume_24h', 'order': 'desc'}],
    limit=10,
  )
  for token in page['list']:
    trend = token['trend_info']
    print(token['symbol'], trend.get('volume_24h'), trend.get('price_change_24h'))
```

`field` is any numeric `trend_info.*` field (`trend_info.price_change_1h`,
`trend_info.tx_count_24h`, ...) or a top-level one such as `liquidity` or `holder_count`.
Price changes are fractions (`0.01` is +1%) and volumes are in USD. `ranking_paged` follows
`next_cursor` across pages.

## Security Audit

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  audit = await client.market.token.risk(
    chain_id='56', address='0x55d398326f99059ff775485246999027b3197955', lan='en'
  )
  print(audit['high_risk_num'], audit['middle_risk_num'], audit['low_risk_num'])
  for item in audit['all_analysis']['high_risk_list']:
    if item['risk_flag'] == '1':  # flagged on this token
      print(item['risk_key'], item['risk_name'])
  print(audit['tax_analysis']['token_tax']['sell_tax'])
  print(audit['data_analysis']['top10_percent'])
```

Every audit item is listed whether or not it is flagged: `risk_flag` is `'1'` when it is,
`'0'` when it is not, and `''` when Gate did not evaluate it (`ignore='true'` hides those).
In `data_analysis`, `top10_percent` and `top100_percent` are percentages while
`max_holder_percent` is a fraction.
