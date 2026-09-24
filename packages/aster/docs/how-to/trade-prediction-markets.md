# Trade Prediction Markets

`client.prediction` has the same market data, trading, account and stream routers as
`client.spot`. Each outcome of a prediction market is its own tradable token, such as
`BTC_UP_DOWN_5M_1790237100_YUSDT`.

## Find Markets

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  info = await client.prediction.market.exchange_info()
  print(info['predictionEvents'][:3])
  print([symbol['symbol'] for symbol in info['symbols'][:5]])
```

## Buy And Sell Outcomes

A market buy can be sized by the quote amount to spend:

```python
from decimal import Decimal

from typed_aster import Aster

async with Aster.new() as client:
  order = await client.prediction.trade.place_order(
    {
      'symbol': 'BTC_UP_DOWN_5M_1790237100_YUSDT',
      'side': 'BUY',
      'type': 'MARKET',
      'quoteOrderQty': Decimal('10'),
    }
  )
  print(order['status'])
```

Query, cancel and list orders exactly as on spot: `client.prediction.trade.order`,
`cancel_order`, `open_orders`, `cancel_all_open_orders`.

## Mint, Burn, Split And Merge

These convert between the quote asset and outcome tokens directly:

```python
from decimal import Decimal

from typed_aster import Aster

async with Aster.new() as client:
  symbol = 'BTC_UP_DOWN_5M_1790237100_YUSDT'
  # quote asset -> equal amounts of YES and NO
  await client.prediction.outcomes.mint(symbol=symbol, quantity=Decimal('5'))
  # equal amounts of YES and NO -> quote asset
  await client.prediction.outcomes.burn(symbol=symbol, quantity=Decimal('5'))
```

For multi-outcome events, `split(event=..., symbol=..., quantity=...)` converts the quote
asset into one market's outcome tokens, and `merge(event=..., quantity=...)` redeems a full set.

## Positions And Settlements

```python
from typed_aster import Aster

async with Aster.new() as client:
  positions = await client.prediction.positions.list()
  closed = await client.prediction.positions.history()
  settled = await client.prediction.positions.settlements()
  print(positions, closed, settled)
```

Prediction requests must reach Aster within 10 seconds of being signed, so keep your clock
in sync.
