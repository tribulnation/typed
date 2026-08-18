"""`private/get_block_trade` — `private/get_block_trade`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class TradeAllocationClientInfo(TypedDict):
  """Optional client allocation info for brokers."""

  client_id: NotRequired[int]
  """ID of a client; available to broker. Represents a group of users under a common name."""
  client_link_id: NotRequired[int]
  """ID assigned to a single user in a client; available to broker."""
  name: NotRequired[str]
  """Name of the linked user within the client; available to broker."""


class TradeAllocation(TypedDict):
  """One allocation of a Block RFQ pre-allocated trade to a user."""

  user_id: NotRequired[int]
  """User ID to which part of the trade is allocated. For brokers the User ID is obstructed."""
  amount: float
  """Amount allocated to this user."""
  fee: float
  """Fee for the allocated part of the trade."""
  client_info: NotRequired[TradeAllocationClientInfo]


class UserTrade(TypedDict):
  """One matched trade that was part of a block trade."""

  trade_id: str
  """Unique (per currency) trade identifier"""
  trade_seq: int
  """The sequence number of the trade within instrument"""
  instrument_name: str
  """Unique instrument identifier"""
  timestamp: int
  """The timestamp of the trade (milliseconds since the UNIX epoch)"""
  starbase_timestamp: NotRequired[int]
  """Optional field: timestamp of the match (trade) in Starbase, in nanoseconds since the UNIX epoch (present only for trades matched in Starbase)"""
  order_type: NotRequired[Literal['limit', 'market', 'liquidation']]
  """Order type: `"limit"`, `"market"`, or `"liquidation"`"""
  advanced: NotRequired[Literal['usd', 'implv']]
  """Advanced type of user order: `"usd"` or `"implv"` (only for options; omitted if not applicable)"""
  order_id: str
  """Id of the user order (maker or taker), i.e. subscriber's order id that took part in the trade"""
  matching_id: str
  """Always `null`"""
  starbase_match_id: NotRequired[int]
  """Optional field containing the Starbase match identifier (present only for trades matched via Starbase)"""
  starbase_order_id: NotRequired[int]
  """Optional field: the id in Starbase of the user's own order (maker or taker side) that took part in the trade; for self-trades this is always the taker order's id, and for combo legs it is the parent combo order's id (present only for trades matched in Starbase)"""
  direction: Literal['buy', 'sell']
  """Trade direction of the taker"""
  tick_direction: Literal[0, 1, 2, 3]
  """Direction of the "tick" (`0` = Plus Tick, `1` = Zero-Plus Tick, `2` = Minus Tick, `3` = Zero-Minus Tick)."""
  index_price: float
  """Index Price at the moment of trade"""
  price: float
  """The price of the trade"""
  amount: float
  """Trade amount. For perpetual and inverse futures the amount is in USD units. For options and linear futures it is the underlying base currency coin."""
  contracts: NotRequired[float]
  """Trade size in contract units (optional, may be absent in historical trades)"""
  iv: NotRequired[float]
  """Option implied volatility for the price (Option only)"""
  underlying_price: NotRequired[float]
  """Underlying price for implied volatility calculations (Options only)"""
  liquidation: NotRequired[Literal['M', 'T', 'MT']]
  """Optional field (only for trades caused by liquidation): `"M"` when maker side of trade was under liquidation, `"T"` when taker side was under liquidation, `"MT"` when both sides of trade were under liquidation"""
  liquidity: NotRequired[Literal['M', 'T']]
  """Describes what was role of users order: `"M"` when it was maker order, `"T"` when it was taker order"""
  fee: float
  """User's fee in units of the specified `fee_currency`"""
  fee_currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR']
  """Currency, i.e `"BTC"`, `"ETH"`, `"USDC"`"""
  label: NotRequired[str]
  """User defined label (presented only when previously set for order by user)"""
  state: Literal['open', 'filled', 'rejected', 'cancelled', 'untriggered', 'archive']
  """Order state: `"open"`, `"filled"`, `"rejected"`, `"cancelled"`, `"untriggered"` or `"archive"` (if order was archived)"""
  block_trade_id: NotRequired[str]
  """Block trade id - when trade was part of a block trade"""
  block_rfq_id: NotRequired[int]
  """ID of the Block RFQ - when trade was part of the Block RFQ"""
  block_rfq_quote_id: NotRequired[int]
  """ID of the Block RFQ quote - when trade was part of the Block RFQ"""
  reduce_only: NotRequired[str]
  """`true` if user order is reduce-only"""
  post_only: NotRequired[str]
  """`true` if user order is post-only"""
  mmp: NotRequired[bool]
  """`true` if user order is MMP"""
  risk_reducing: NotRequired[bool]
  """`true` if user order is marked by the platform as a risk reducing order (can apply only to orders placed by PM users)"""
  api: NotRequired[bool]
  """`true` if user order was created with API"""
  profit_loss: NotRequired[float]
  """Profit and loss in base currency."""
  mark_price: float
  """Mark Price at the moment of trade"""
  combo_id: NotRequired[str]
  """Optional field containing combo instrument name if the trade is a combo trade"""
  combo_trade_id: NotRequired[str]
  """Optional field containing combo trade identifier if the trade is a combo trade"""
  quote_set_id: NotRequired[str]
  """QuoteSet of the user order (optional, present only for orders placed with `private/mass_quote`)"""
  quote_id: NotRequired[str]
  """QuoteID of the user order (optional, present only for orders placed with `private/mass_quote`)"""
  trade_allocations: NotRequired[list[TradeAllocation]]
  """List of allocations for Block RFQ pre-allocation. Each allocation specifies `user_id`, `amount`, and `fee` for the allocated part of the trade. For broker client allocations, a `client_info` object will be included."""


class BlockTrade(TypedDict):
  """One executed block trade."""

  id: str
  """Block trade id"""
  timestamp: int
  """The timestamp (milliseconds since the Unix epoch)"""
  trades: list[UserTrade]
  """The individual fills that make up this block trade."""
  app_name: NotRequired[str]
  """The name of the application that executed the block trade on behalf of the user (optional)."""
  broker_code: NotRequired[str]
  """Broker code associated with the broker block trade."""
  broker_name: NotRequired[str]
  """Name of the broker associated with the block trade."""


validate_get_block_trade = validator[BlockTrade](BlockTrade)


class GetBlockTrade(RpcEndpoint):
  """`private/get_block_trade`."""

  async def get_block_trade(
    self, *, id: str, validate: bool | None = None
  ) -> BlockTrade:
    """Returns information about a specific block trade identified by `block_trade_id`.

    Scope: `block_trade:read`.

    Args:
      id: Block trade id
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/block-trade/private-get_block_trade)
    """
    params: dict = {
      'id': id,
    }
    return await self.authed_request(
      'private/get_block_trade',
      params=params,
      validator=validate_get_block_trade,
      validate=validate,
    )
