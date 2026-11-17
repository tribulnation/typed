"""The order appendix: a `uint128` bitfield carrying an order's type and flags.

Bit layout, most to least significant (version 1):

| value | builder id | builder fee rate | reserved | trigger | reduce-only | order type | isolated | version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 127-64 | 63-48 | 47-38 | 37-14 | 13-12 | 11 | 10-9 | 8 | 7-0 |

`value` is a TWAP's execution count (high 32 bits) and maximum slippage times 1e6 (low 32
bits), or an isolated order's margin times 1e6, and `0` otherwise.
"""

from typing_extensions import Literal, overload
from decimal import Decimal

from .exc import BadRequest

OrderType = Literal['default', 'ioc', 'fok', 'post_only']
"""Time in force: `default` rests on the book (GTC), `ioc` fills what it can immediately
and cancels the rest, `fok` fills entirely or not at all, `post_only` only ever rests."""

AppendixTrigger = Literal['price', 'twap', 'twap_custom_amounts']
"""Trigger service routing: a price condition, a TWAP of equal slices, or a TWAP whose
slice amounts the trigger order lists itself."""

VERSION = 1
"""The appendix layout version this module packs."""

ORDER_TYPES: dict[OrderType, int] = {'default': 0, 'ioc': 1, 'fok': 2, 'post_only': 3}
"""Order type -> its 2-bit code."""

TRIGGERS: dict[AppendixTrigger, int] = {'price': 1, 'twap': 2, 'twap_custom_amounts': 3}
"""Trigger type -> its 2-bit code (`0` is no trigger)."""

X6 = Decimal(10) ** 6
"""Scale of the appendix's fixed-point margin and slippage."""


def bounded(value: int, *, bits: int, field: str) -> int:
  """`value`, checked to fit `bits` unsigned bits.

  Raises:
    BadRequest: The value is negative or too wide.
  """
  if isinstance(value, bool) or not isinstance(value, int):
    raise BadRequest(f'{field} must be an integer, got {value!r}')
  if not 0 <= value < 1 << bits:
    raise BadRequest(f'{field} must fit {bits} unsigned bits, got {value}')
  return value


def scaled_x6(value: Decimal | int | str, *, bits: int, field: str) -> int:
  """A decimal amount times 1e6, exactly.

  Raises:
    BadRequest: The value is not a finite decimal, has more than 6 decimals, or does not
      fit `bits` unsigned bits once scaled.
  """
  if isinstance(value, (bool, float)):
    raise BadRequest(f'{field} must be a Decimal, int or numeral string, got {value!r}')
  try:
    amount = Decimal(value)
  except ArithmeticError:
    raise BadRequest(f'{field} must be a decimal, got {value!r}') from None
  if not amount.is_finite():
    raise BadRequest(f'{field} must be finite, got {value!r}')
  raw = amount * X6
  if raw != raw.to_integral_value():
    raise BadRequest(f'{field} has more than 6 decimals: {value!r}')
  return bounded(int(raw), bits=bits, field=field)


@overload
def order_appendix(
  order_type: OrderType = 'default',
  *,
  reduce_only: bool = False,
  isolated_margin: Decimal | int | str | None = None,
  trigger: Literal['price'] | None = None,
  builder_id: int = 0,
  builder_fee_rate: int = 0,
) -> int: ...
@overload
def order_appendix(
  order_type: Literal['ioc'] = 'ioc',
  *,
  reduce_only: bool = False,
  trigger: Literal['twap', 'twap_custom_amounts'],
  twap_executions: int,
  twap_slippage: Decimal | int | str,
  builder_id: int = 0,
  builder_fee_rate: int = 0,
) -> int: ...
def order_appendix(
  order_type: OrderType | None = None,
  *,
  reduce_only: bool = False,
  isolated_margin: Decimal | int | str | None = None,
  trigger: AppendixTrigger | None = None,
  twap_executions: int | None = None,
  twap_slippage: Decimal | int | str | None = None,
  builder_id: int = 0,
  builder_fee_rate: int = 0,
) -> int:
  """Pack an order appendix (version 1), the `appendix` of a signed order.

  An order is either isolated or a TWAP, never both: both use the appendix's upper 64 bits.

  Args:
    order_type: Time in force; `default` (GTC) unless a TWAP, which Nado requires to be
      `ioc` (its default there).
    reduce_only: Only ever reduce the position.
    isolated_margin: Trade in an isolated subaccount, moving this much USDT0 margin (at most
      6 decimals) into it on first match; `None` trades cross-margin.
    trigger: Route the order through the trigger service: `price` for a stop or take-profit
      (with `trigger={'price_trigger': ...}`), `twap`/`twap_custom_amounts` for a TWAP
      (with `trigger={'time_trigger': ...}`).
    twap_executions: Number of TWAP slices.
    twap_slippage: Maximum slippage of each TWAP slice against the oracle price, as a
      fraction (`'0.01'` is 1%, at most 6 decimals).
    builder_id: Registered builder to share fees with; `0` for none.
    builder_fee_rate: Builder fee, in 0.1 bps of notional (`0`-`1023`).

  Returns:
    The appendix, an unsigned 128-bit integer.

  Raises:
    BadRequest: A field is out of range, or the combination is invalid.

  Examples:
    ```python
    order_appendix('post_only')  # 1537
    order_appendix('post_only', trigger='price')  # 5633
    order_appendix(trigger='twap', twap_executions=10, twap_slippage='0.005')  # ioc
    ```
  """
  twap = trigger in ('twap', 'twap_custom_amounts')
  if order_type is None:
    order_type = 'ioc' if twap else 'default'
  if order_type not in ORDER_TYPES:
    raise BadRequest(
      f'order_type must be one of {list(ORDER_TYPES)}, got {order_type!r}'
    )
  if trigger is not None and trigger not in TRIGGERS:
    raise BadRequest(f'trigger must be one of {list(TRIGGERS)}, got {trigger!r}')
  if twap:
    if order_type != 'ioc':
      raise BadRequest(f"A TWAP's order_type must be 'ioc', got {order_type!r}")
    if isolated_margin is not None:
      raise BadRequest('An order cannot be both isolated and a TWAP')
    if twap_executions is None or twap_slippage is None:
      raise BadRequest('A TWAP needs twap_executions and twap_slippage')
    executions = bounded(twap_executions, bits=32, field='twap_executions')
    slippage = scaled_x6(twap_slippage, bits=32, field='twap_slippage')
    value = executions << 32 | slippage
  else:
    if twap_executions is not None or twap_slippage is not None:
      raise BadRequest('twap_executions and twap_slippage need a TWAP trigger')
    value = (
      0
      if isolated_margin is None
      else scaled_x6(isolated_margin, bits=64, field='isolated_margin')
    )
  return (
    value << 64
    | bounded(builder_id, bits=16, field='builder_id') << 48
    | bounded(builder_fee_rate, bits=10, field='builder_fee_rate') << 38
    | (TRIGGERS[trigger] if trigger is not None else 0) << 12
    | int(reduce_only) << 11
    | ORDER_TYPES[order_type] << 9
    | int(isolated_margin is not None) << 8
    | VERSION
  )
