# Listen To Streams

`client.uta_streams` is UTA v3's WebSocket feed. Each subscription returns a `StreamManager`:
use it as an async context manager to auto-unsubscribe on exit.

## Public: Ticker

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  async with client.uta_streams.ticker(inst_type='spot', symbol='BTCUSDT') as stream:
    async for push in stream:
      print(push['data'])
```

`inst_type` is lowercase on UTA's WebSocket (`spot`, `usdt-futures`, `coin-futures`,
`usdc-futures`), a different casing from REST's `category`.

## Public: Order Book & Trades

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  async with client.uta_streams.orderbook(depth='5', inst_type='spot', symbol='BTCUSDT') as stream:
    async for push in stream:
      print(push['data'])

  async with client.uta_streams.trade(inst_type='spot', symbol='BTCUSDT') as stream:
    async for push in stream:
      print(push['data'])
```

`depth` is `''` for full-depth incremental updates, or `'1'`/`'5'`/`'50'` for a fixed number of
re-snapshotted merged levels.

## Private: Account, Orders, Fills

Private channels need credentials and all subscribe under the fixed `inst_type='UTA'`. UTA v3
doesn't split private channels by product category the way Classic v2 does.

```python
from bitget import Bitget

async with Bitget.new() as client:
  async with client.uta_streams.account(inst_type='UTA') as stream:
    async for push in stream:
      print(push['data'])

  async with client.uta_streams.orders(inst_type='UTA') as stream:
    async for push in stream:
      print(push['data'])

  async with client.uta_streams.fill(inst_type='UTA') as stream:
    async for push in stream:
      print(push['data'])
```

## Reconnects

Bitget disconnects idle connections after 2 minutes without a ping, and force-closes every
connection every 24 hours regardless. Expect and handle reconnects for long-running
subscriptions.

## Classic v2

`client.classic_streams` mirrors the same shape for Classic-mode accounts, with uppercase
`inst_type` (`SPOT`, `USDT-FUTURES`, ...) and channels split per product category rather than a
fixed `UTA`:

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  async with client.classic_streams.ticker(inst_type='SPOT', inst_id='BTCUSDT') as stream:
    async for push in stream:
      print(push['data'])
```
