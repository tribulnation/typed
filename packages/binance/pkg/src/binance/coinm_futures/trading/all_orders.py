from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMOrder(TypedDict):
  """An order."""

  avgPrice: NotRequired[str]
  """Average execution price."""
  clientOrderId: NotRequired[str]
  """Client order ID."""
  cumBase: NotRequired[str]
  """Cumulative filled quantity denominated in the pair's base asset."""
  cumQuote: NotRequired[str]
  """Cumulative filled quantity denominated in the quote asset."""
  executedQty: NotRequired[str]
  """Executed quantity, in contracts."""
  orderId: int
  """Order ID."""
  origQty: NotRequired[str]
  """Original order quantity, in contracts."""
  origType: NotRequired[
    Literal[
      'LIMIT',
      'MARKET',
      'STOP',
      'STOP_MARKET',
      'TAKE_PROFIT',
      'TAKE_PROFIT_MARKET',
      'TRAILING_STOP_MARKET',
    ]
  ]
  """Original order type."""
  price: NotRequired[str]
  """Order price."""
  reduceOnly: NotRequired[bool]
  """Whether the order is reduce-only."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Order side."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """Position side."""
  status: Literal['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'EXPIRED']
  """Order status. Documented closed set (COIN-M common-definition doc)."""
  stopPrice: NotRequired[str]
  """Stop trigger price. Ignored when order type is TRAILING_STOP_MARKET."""
  closePosition: NotRequired[bool]
  """Whether the order closes the whole position (Close-All)."""
  symbol: str
  """Symbol."""
  pair: NotRequired[str]
  """Underlying pair."""
  time: NotRequired[int]
  """Order creation time."""
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'GTX']]
  """Time in force."""
  type: NotRequired[
    Literal[
      'LIMIT',
      'MARKET',
      'STOP',
      'STOP_MARKET',
      'TAKE_PROFIT',
      'TAKE_PROFIT_MARKET',
      'TRAILING_STOP_MARKET',
    ]
  ]
  """Order type. See `notes` — after the CM/UM migration this endpoint rejects the five stop-type values with -4120; only LIMIT and MARKET are currently accepted here."""
  activatePrice: NotRequired[str]
  """Activation price. Only returned for TRAILING_STOP_MARKET orders."""
  priceRate: NotRequired[str]
  """Callback rate. Only returned for TRAILING_STOP_MARKET orders."""
  updateTime: NotRequired[int]
  """Last update time."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """stopPrice trigger price type."""
  priceProtect: NotRequired[bool]
  """Whether the conditional order's trigger is price-protected."""
  priceMatch: NotRequired[str]
  """Price match mode."""
  selfTradePreventionMode: NotRequired[str]
  """Self-trade prevention mode."""
  goodTillDate: NotRequired[int]
  """Auto-cancel time for a GTD order."""


class AllOrders(RpcEndpoint):
  """All Orders"""

  async def all_orders(
    self,
    *,
    symbol: str | None = None,
    pair: str | None = None,
    order_id: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[CoinMOrder]:
    """Get all account orders — active, canceled, or filled. A canceled/expired order with no fills drops out of this history 3 days after creation; every order drops out 90 days after creation.

    Args:
      symbol: Symbol.
      pair: Underlying pair. Cannot be sent together with `orderId`.
      order_id: If set, returns orders with ID >= this value; otherwise the most recent orders are returned.
      start_time: Start time.
      end_time: End time. The query window must be under 7 days (default: the most recent 7 days).
      limit: Maximum number of records to return.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#all-orders)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if pair is not None:
      params['pair'] = pair
    if order_id is not None:
      params['orderId'] = order_id
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    _Response = list[CoinMOrder]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/dapi/v1/allOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
