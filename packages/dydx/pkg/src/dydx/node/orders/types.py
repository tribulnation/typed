"""Typed dYdX order parameters."""

from decimal import Decimal
from typing_extensions import Literal, NotRequired, TypedDict

from dydx.indexer.types.market import PerpetualMarket
from dydx.node.market import Market

DecimalValue = Decimal | str | int
Side = Literal['BUY', 'SELL']
TimeInForce = Literal['GOOD_TIL_TIME', 'IMMEDIATE_OR_CANCEL', 'POST_ONLY', 'FILL_OR_KILL']
ConditionType = Literal['TAKE_PROFIT', 'STOP_LOSS']
Flags = Literal['LONG_TERM', 'SHORT_TERM', 'CONDITIONAL']

class OrderParams(TypedDict):
  """Ergonomic dYdX order parameters."""

  side: Side
  """Order side."""
  size: DecimalValue
  """Human-readable base asset size."""
  price: DecimalValue
  """Human-readable order price."""
  flags: Flags
  """dYdX order flag category."""
  time_in_force: NotRequired[TimeInForce]
  """Optional dYdX time-in-force behavior."""
  client_metadata: NotRequired[int]
  """Optional client metadata integer included in the protocol order."""
  condition_type: NotRequired[ConditionType]
  """Optional conditional order trigger type."""
  conditional_order_trigger_subticks: NotRequired[int]
  """Optional conditional trigger price expressed as protocol subticks."""
  client_id: NotRequired[int]
  """Optional client-generated order ID."""
  reduce_only: NotRequired[bool]
  """Whether the order may only reduce exposure."""
  good_til_block: NotRequired[int]
  """Optional short-term expiry block."""
  good_til_block_time: NotRequired[int]
  """Optional stateful expiry timestamp."""

class OrderPlacement(TypedDict):
  """One dYdX order placement inside a multi-order transaction."""

  market: Market | PerpetualMarket
  """Market metadata used to convert price and size into protocol values."""
  order: OrderParams
  """Order parameters for the CLOB message."""
  subaccount: NotRequired[int]
  """Optional dYdX subaccount number under the signing wallet."""
