# Timestamps

Every timestamp is a timezone-aware UTC `datetime`, in requests and responses alike. Gate's
wire format varies by call, epoch seconds or RFC 3339 strings, and the client converts both
ways for you.

## Responses

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  price = await client.market.price(
    chain_id=1, token_address='0xdac17f958d2ee523a2206206994597c13d831ec7'
  )
  print(price['time'])  # datetime
  candles = await client.market.candles(
    chain_id=1, token_address='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', period=60
  )
  print(candles[0]['ts'])  # datetime: the candle's open time
```

## Requests

Range parameters take a `datetime` directly:

```python
from datetime import datetime, timedelta, timezone
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  end = datetime.now(timezone.utc)
  candles = await client.market.candles(
    chain_id=1,
    token_address='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    period=300,
    start=end - timedelta(hours=6),
    end=end,
  )
  created = await client.market.token.created(start=end - timedelta(hours=1), end=end)
```

Pass timezone-aware values. A naive `datetime` is read as local time for the epoch-second
bounds of `candles` but as UTC for the RFC 3339 bounds of `token.created`.

## Wire Formats

| Wire format | Fields |
| --- | --- |
| Epoch seconds | `market.price` `time`; candle `ts` and the `candles` `start`/`end` bounds; `trade.build` `ts`; `token.trade_info` `price_update_ts`; liquidity event `block_timestamp`; `volume_stats` `timestamp`; `token.ranking` `risk_info_update_ts` |
| RFC 3339 | `token.created` `start`/`end` bounds; token `created_at`/`updated_at`; order `creationTime`/`endTime` |

Gate's candle bounds are seconds, never milliseconds; the client sends them in the right unit
whatever `datetime` you pass.
