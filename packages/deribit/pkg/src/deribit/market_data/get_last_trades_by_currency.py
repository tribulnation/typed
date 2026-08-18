"""`public/get_last_trades_by_currency` — `public/get_last_trades_by_currency`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Trade(TypedDict):
  """One executed trade."""

  trade_id: str
  """Unique (per currency) trade identifier"""
  trade_seq: int
  """The sequence number of the trade within instrument"""
  instrument_name: str
  """Unique instrument identifier"""
  timestamp: int
  """The timestamp of the trade (milliseconds since the UNIX epoch)"""
  starbase_timestamp: NotRequired[int]
  """The Starbase causal timestamp of the trade (nanoseconds since the Unix epoch)"""
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
  liquidation: NotRequired[Literal['M', 'T', 'MT']]
  """Optional field (only for trades caused by liquidation): `"M"` when maker side of trade was under liquidation, `"T"` when taker side was under liquidation, `"MT"` when both sides of trade were under liquidation"""
  mark_price: float
  """Mark Price at the moment of trade"""
  block_trade_id: NotRequired[str]
  """Block trade id - when trade was part of a block trade"""
  block_trade_leg_count: NotRequired[int]
  """Block trade leg count - when trade was part of a block trade"""
  combo_id: NotRequired[str]
  """Optional field containing combo instrument name if the trade is a combo trade"""
  combo_trade_id: NotRequired[str]
  """Optional field containing combo trade identifier if the trade is a combo trade"""
  starbase_match_id: NotRequired[int]
  """Optional field containing the Starbase match identifier (present only for trades matched via Starbase)"""
  block_rfq_id: NotRequired[int]
  """ID of the Block RFQ - when trade was part of the Block RFQ"""


class TradesPage(TypedDict):
  """A page of trades."""

  trades: list[Trade]
  """Trades matching the query, this page."""
  has_more: bool
  """Whether more trades exist beyond this page within the requested range/sequence window."""


validate_get_last_trades_by_currency = validator[TradesPage](TradesPage)


class GetLastTradesByCurrency(RpcEndpoint):
  """`public/get_last_trades_by_currency`."""

  async def get_last_trades_by_currency(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    kind: Literal[
      'future', 'option', 'spot', 'future_combo', 'option_combo', 'combo', 'any'
    ]
    | None = None,
    start_id: str | None = None,
    end_id: str | None = None,
    start_timestamp: int | None = None,
    end_timestamp: int | None = None,
    count: int | None = None,
    sorting: Literal['asc', 'desc', 'default'] | None = None,
    validate: bool | None = None,
  ) -> TradesPage:
    """Retrieves the latest trades that have occurred for instruments in a specific currency. Returns trade details including price, amount, direction, timestamp, and trade ID for all instruments in the currency.

    Results can be filtered by instrument kind and trade ID range or timestamp range. Use the `count` parameter to limit the number of trades returned, and `sorting` to control the order (ascending or descending by trade ID).

    Args:
      currency: The currency symbol
      kind: Instrument kind, `"combo"` for any combo or `"any"` for all. If not provided instruments of all kinds are considered
      start_id: The ID of the first trade to be returned. Number for BTC trades, or hyphen name in ex. `"ETH-15"` # `"ETH_USDC-16"`
      end_id: The ID of the last trade to be returned. Number for BTC trades, or hyphen name in ex. `"ETH-15"` # `"ETH_USDC-16"`
      start_timestamp: The earliest timestamp to return result from (milliseconds since the UNIX epoch). When param is provided trades are returned from the earliest
      end_timestamp: The most recent timestamp to return result from (milliseconds since the UNIX epoch). Only one of params: start_timestamp, end_timestamp is truly required
      count: Number of requested items, default - `10`, maximum - `1000`
      sorting: Direction of results sorting (`default` value means no sorting, results will be returned in order in which they left the database)
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_last_trades_by_currency)
    """
    params: dict = {
      'currency': currency,
    }
    if kind is not None:
      params['kind'] = kind
    if start_id is not None:
      params['start_id'] = start_id
    if end_id is not None:
      params['end_id'] = end_id
    if start_timestamp is not None:
      params['start_timestamp'] = start_timestamp
    if end_timestamp is not None:
      params['end_timestamp'] = end_timestamp
    if count is not None:
      params['count'] = count
    if sorting is not None:
      params['sorting'] = sorting
    return await self.request(
      'public/get_last_trades_by_currency',
      params=params,
      validator=validate_get_last_trades_by_currency,
      validate=validate,
    )
