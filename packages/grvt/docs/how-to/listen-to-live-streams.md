# Listen To Live Streams

GRVT pushes market data on a public WebSocket (`client.market_streams`) and your own account
events on an authenticated one (`client.trading_streams`). Each socket connects on first use
and carries every subscription of its kind.

## Public Market Streams

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  async with client.market_streams.mini_ticker('BTC_USDT_Perp', rate=500) as stream:
    async for mini in stream:
      print(
        mini.get('mark_price'), mini.get('best_bid_price'), mini.get('best_ask_price')
      )
```

Leaving the `async with` block unsubscribes. To manage the subscription yourself, `await`
it and unsubscribe explicitly:

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  stream = await client.market_streams.trades('BTC_USDT_Perp')
  count = 0
  async for trade in stream:
    print(trade['price'], trade['size'], trade['is_taker_buyer'])
    count += 1
    if count == 10:
      break
  await stream.unsubscribe()
```

Available market streams:

| Method | Feed | Options |
| --- | --- | --- |
| `mini_ticker` | full snapshot on every message | `rate`: 200, 500, 1000, 5000 |
| `ticker` | full snapshot on every message | `rate`: 500, 1000, 5000 |
| `mini_ticker_delta` | one snapshot, then only changed fields | `rate`: 0, 50, 100, 200, 500, 1000, 5000 |
| `ticker_delta` | one snapshot, then only changed fields | `rate`: 100, 200, 500, 1000, 5000 |
| `orderbook` | full book snapshot on every message | `rate`: 500, 1000; `depth`: 10, 50, 100, 500 |
| `orderbook_delta` | one full book, then changed levels (`size` `0` removes a level) | `rate`: 50, 100, 250, 500, 1000 |
| `trades` | the most recent `limit` trades, then every new trade | `limit`: 50 (default), 200, 500, 1000 |
| `candlesticks` | candle updates | `interval`, `type` |

`rate` is in milliseconds: the interval between two snapshots, or the minimum interval
between two deltas (`0` sends every change as it happens). Every option except `limit` is
required, and a value outside its list does not type-check.

## Your Orders, Fills And Positions

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  async with client.trading_streams.orders(instrument='BTC_USDT_Perp') as stream:
    async for order in stream:
      state = order.get('state')
      print(order['metadata']['client_order_id'], state and state['status'])
```

Private streams need credentials (see [API Keys Setup](../api-keys.md)).

| Method | Feed | Filters |
| --- | --- | --- |
| `orders` | full order updates | `sub_account_id`, `instrument` |
| `order_states` | order state changes only | `sub_account_id`, `instrument` |
| `fills` | your executed trades | `sub_account_id`, `instrument` |
| `positions` | position changes | `sub_account_id`, `instrument` |
| `rfqs`, `rfq_quotes` | RFQ requests and quotes | `sub_account_id`, `instrument` |
| `ecn_to_broker` | `STABLE_PERP` order updates, for qualified market makers | `sub_account_id`, `instrument` |
| `cancels` | expiries of cancels sent with a `time_to_live_ms` | `sub_account_id` |
| `transfers` | transfers to or from an account | `main_account_id`, `sub_account_id` |
| `deposits`, `withdrawals` | deposits to and withdrawals from a main account | `main_account_id` |

A left-out `sub_account_id` is the configured trading sub-account, except on `transfers`,
where leaving it out follows the whole main account. Leave `instrument` out to receive every
instrument. `main_account_id` is the `main_account_id` of `funding_account_summary()`; a
checksummed address works too, since the client lowercases it as GRVT requires.

## Delivery Guarantees

1. Each message is validated against its type, like an HTTP reply.
2. GRVT numbers every message. A repeated message is dropped. A gap or a decrease ends the
   stream with `NetworkError`, because the feed can no longer be trusted, and a message with
   no sequence number ends it with `ValidationError`. Subscribe again to resume.
3. One live subscription per stream and instrument. On a market stream, every option after
   the instrument (`rate`, `depth`, `limit`, a candle's `interval` and `type`) belongs to
   that one subscription: subscribing the same stream and instrument with any other options,
   such as a second candle interval, raises `BadRequest`, since GRVT would silently replace
   the first. An identical second subscription raises `BadRequest` too. Unsubscribe first.
   Different streams (`ticker` and `ticker_delta`, say) or instruments do not conflict.
