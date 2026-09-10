"""Typed dYdX order parameters."""

from decimal import Decimal

from typing_extensions import Literal, NotRequired, TypedDict

from typed_dydx.indexer.schemas import PerpetualMarket
from typed_dydx.node.market import Market

DecimalValue = Decimal | str | int
Side = Literal['BUY', 'SELL']
TimeInForce = Literal['GOOD_TIL_TIME', 'IMMEDIATE_OR_CANCEL', 'POST_ONLY', 'FILL_OR_KILL']
ConditionType = Literal['TAKE_PROFIT', 'STOP_LOSS']
Flags = Literal['LONG_TERM', 'SHORT_TERM', 'CONDITIONAL']

class BaseOrderParams(TypedDict):
  """Order fields shared by every dYdX order flag category."""

  side: Side
  """Order side."""
  size: DecimalValue
  """Human-readable base asset size."""
  price: DecimalValue
  """Human-readable order price."""
  time_in_force: NotRequired[TimeInForce]
  """Optional dYdX time-in-force behavior."""
  client_metadata: NotRequired[int]
  """Optional client metadata integer included in the protocol order."""
  client_id: NotRequired[int]
  """Optional client-generated order ID."""
  reduce_only: NotRequired[bool]
  """Whether the order may only reduce exposure."""

class ShortTermOrderParams(BaseOrderParams):
  """Ergonomic parameters for a short-term dYdX order."""

  flags: Literal['SHORT_TERM']
  """dYdX order flag category."""
  good_til_block: NotRequired[int]
  """Optional short-term expiry block."""

class LongTermOrderParams(BaseOrderParams):
  """Ergonomic parameters for a long-term (stateful) dYdX order."""

  flags: Literal['LONG_TERM']
  """dYdX order flag category."""
  good_til_block_time: NotRequired[int]
  """Optional stateful expiry timestamp."""

class ConditionalOrderParams(BaseOrderParams):
  """Ergonomic parameters for a conditional (stateful) dYdX order."""

  flags: Literal['CONDITIONAL']
  """dYdX order flag category."""
  good_til_block_time: NotRequired[int]
  """Optional stateful expiry timestamp."""
  condition_type: NotRequired[ConditionType]
  """Optional conditional order trigger type."""
  conditional_order_trigger_subticks: NotRequired[int]
  """Optional conditional trigger price expressed as protocol subticks."""

OrderParams = ShortTermOrderParams | LongTermOrderParams | ConditionalOrderParams
"""Ergonomic dYdX order parameters, narrowed by `flags`."""

class OrderPlacement(TypedDict):
  """One dYdX order placement inside a multi-order transaction."""

  market: Market | PerpetualMarket
  """Market metadata used to convert price and size into protocol values."""
  order: OrderParams
  """Order parameters for the CLOB message."""
  subaccount: NotRequired[int]
  """Optional dYdX subaccount number under the signing wallet."""
