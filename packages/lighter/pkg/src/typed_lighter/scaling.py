"""`Scaler`: converts between decimal prices and sizes and the scaled integers transactions take.

A Lighter transaction carries prices and sizes as integers: `price * 10^supported_price_decimals`
and `size * 10^supported_size_decimals`, per market (`orderBookDetails`). `client.scaler(id)`
fetches those decimals once; the returned `Scaler` then converts locally, in both directions,
for perp and spot markets alike. A value with more decimals than the market supports raises
`BadRequest` unless a `rounding` is given, so a price never moves silently.
"""

from typing_extensions import Literal
from dataclasses import dataclass
from decimal import (
  ROUND_CEILING,
  ROUND_FLOOR,
  ROUND_HALF_EVEN,
  Decimal,
  InvalidOperation,
  localcontext,
)

from .api.markets.order_book_details import (
  OrderBookDetailsEndpoint,
  PerpsOrderBookDetail,
  SpotOrderBookDetail,
)
from .core.exc import BadRequest
from .core.transport.http import HttpRpcClient

Rounding = Literal['floor', 'ceiling', 'half-even']
"""How to round a value with more decimals than the market supports: towards negative
infinity, towards positive infinity, or to the nearest (ties to even)."""

ROUNDINGS: dict[Rounding, str] = {
  'floor': ROUND_FLOOR,
  'ceiling': ROUND_CEILING,
  'half-even': ROUND_HALF_EVEN,
}


def scale(
  value: Decimal | int, *, decimals: int, rounding: Rounding | None, what: str
) -> int:
  """`value * 10^decimals` as an integer.

  Args:
    value: The value to scale.
    decimals: How many decimals to scale it by.
    rounding: How to round a value with more decimals; `None` refuses to round.
    what: What `value` is, for error messages.

  Raises:
    BadRequest: `value` is not finite, or has more than `decimals` decimals and no
      `rounding` was given.
  """
  number = Decimal(value)
  if not number.is_finite():
    raise BadRequest(f'{what} is not a finite number: {value}')
  with localcontext() as context:
    context.prec = max(context.prec, len(number.as_tuple().digits) + decimals + 2)
    scaled = number.scaleb(decimals)
    try:
      integral = scaled.to_integral_value(
        rounding=ROUNDINGS[rounding] if rounding is not None else ROUND_HALF_EVEN
      )
    except InvalidOperation:
      raise BadRequest(f'{what} cannot be scaled: {value}') from None
  if rounding is None and integral != scaled:
    raise BadRequest(
      f'{what} {value} has more than {decimals} decimals; pass `rounding` to round it'
    )
  return int(integral)


def unscale(value: int, *, decimals: int) -> Decimal:
  """`value / 10^decimals`, exactly.

  Args:
    value: The scaled integer.
    decimals: How many decimals it is scaled by.
  """
  return Decimal(value).scaleb(-decimals)


@dataclass(frozen=True, kw_only=True)
class Scaler:
  """Converts one market's prices and sizes to and from the integers transactions take.

  Examples:
    ```python
    from decimal import Decimal

    scaler = await client.scaler(0)
    order = {
      'order_type': 'limit',
      'market_index': scaler.market_id,
      'client_order_index': 1,
      'base_amount': scaler.size(Decimal('0.01')),
      'price': scaler.price(Decimal('2500.5')),
      'is_ask': False,
      'time_in_force': 'post-only',
    }
    ```
  """

  market_id: int
  """Market the decimals belong to."""
  symbol: str
  """Market symbol, for messages."""
  price_decimals: int
  """`supported_price_decimals`: a price is scaled by `10^price_decimals`."""
  size_decimals: int
  """`supported_size_decimals`: a size is scaled by `10^size_decimals`."""

  @classmethod
  def from_details(
    cls, details: PerpsOrderBookDetail | SpotOrderBookDetail
  ) -> 'Scaler':
    """A scaler from a market's `orderBookDetails` entry (perp or spot)."""
    return cls(
      market_id=details['market_id'],
      symbol=details['symbol'],
      price_decimals=details['supported_price_decimals'],
      size_decimals=details['supported_size_decimals'],
    )

  @classmethod
  async def fetch(
    cls, client: HttpRpcClient, market_id: int, *, validate: bool | None = None
  ) -> 'Scaler':
    """Fetch one market's decimals (`GET /api/v1/orderBookDetails`) and build its scaler.

    Args:
      client: The main REST transport.
      market_id: Perp or spot market id.
      validate: Override response validation for the one request.

    Raises:
      BadRequest: The venue does not know the market.
    """
    details = await OrderBookDetailsEndpoint(client=client).order_book_details(
      market_id, validate=validate
    )
    for entry in [*details['order_book_details'], *details['spot_order_book_details']]:
      if entry['market_id'] == market_id:
        return cls.from_details(entry)
    raise BadRequest(f'Unknown market: {market_id}')

  def price(self, value: Decimal | int, *, rounding: Rounding | None = None) -> int:
    """A price as the scaled integer an order's `price`/`trigger_price` takes.

    Args:
      value: The price.
      rounding: Round a price with too many decimals this way instead of raising.

    Raises:
      BadRequest: The price has more decimals than the market supports (and no
        `rounding` was given), or is not finite.
    """
    return scale(
      value,
      decimals=self.price_decimals,
      rounding=rounding,
      what=f'{self.symbol} price',
    )

  def size(self, value: Decimal | int, *, rounding: Rounding | None = None) -> int:
    """A size as the scaled integer an order's `base_amount` takes.

    Args:
      value: The size, in base units.
      rounding: Round a size with too many decimals this way instead of raising.

    Raises:
      BadRequest: The size has more decimals than the market supports (and no
        `rounding` was given), or is not finite.
    """
    return scale(
      value, decimals=self.size_decimals, rounding=rounding, what=f'{self.symbol} size'
    )

  def price_of(self, value: int) -> Decimal:
    """The price a scaled integer stands for (the inverse of `price`).

    Args:
      value: A scaled `price`/`trigger_price`.
    """
    return unscale(value, decimals=self.price_decimals)

  def size_of(self, value: int) -> Decimal:
    """The size a scaled integer stands for (the inverse of `size`).

    Args:
      value: A scaled `base_amount`.
    """
    return unscale(value, decimals=self.size_decimals)
