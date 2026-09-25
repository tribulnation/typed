# Numbers

Lighter sends numbers in three forms, and the client keeps each one as exact as the wire
allows.

## Decimal Strings Are `Decimal`

Balances, prices, sizes and PnL that Lighter sends as strings (`"2650.25"`) arrive as
`decimal.Decimal`, exact to the digit. A few of them are `""` when there is no value (a
market's `mid_price` with an empty book side, an account's `referral_points_percentage`
when unset), so their type is `Decimal | Literal['']`: compare against `''` before doing
arithmetic with one of those.

## JSON Numbers Are `float`

Some fields are JSON numbers on the wire, not strings: candle prices and volumes, funding
rates across venues, the PnL and volume series, the live figures in `order_book_details`
such as `last_trade_price`. They stay `float`. By the time a JSON number reaches Python it
has already been read as a binary floating-point value, so turning it into a `Decimal`
would only dress up a rounded number as an exact one. Round such values yourself, to the
precision you need, before doing money arithmetic with them.

## Transactions Take Scaled Integers

Transactions carry prices and sizes as integers: `price * 10^supported_price_decimals` and
`size * 10^supported_size_decimals`, per market. `client.scaler(market_id)` fetches those
decimals once and converts both ways, for perp and spot markets alike:

```python
from decimal import Decimal

from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  eth = await client.scaler(0)
  price = eth.price(Decimal('2650.25'))  # 265025 with 2 price decimals
  size = eth.size(Decimal('0.05'))  # 500 with 4 size decimals
  print(eth.price_of(price), eth.size_of(size))  # back to 2650.25 and 0.05
```

A value with more decimals than the market supports raises `BadRequest` instead of being
rounded behind your back. Pass `rounding='floor'`, `'ceiling'` or `'half-even'` to round it
explicitly:

```python
from decimal import Decimal

from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  eth = await client.scaler(0)
  bid = eth.price(Decimal('2650.257'), rounding='floor')  # 265025
  ask = eth.price(Decimal('2650.251'), rounding='ceiling')  # 265026
```
