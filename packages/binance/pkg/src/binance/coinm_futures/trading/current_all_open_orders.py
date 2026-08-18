from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMOpenOrder(TypedDict):
  """An open order."""

  avgPrice: NotRequired[str]
  """Average execution price."""
  clientOrderId: NotRequired[str]
  """Client order ID."""
  cumBase: NotRequired[str]
  """Cumulative filled quantity denominated in the pair's base asset."""
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


class CurrentAllOpenOrders(RpcEndpoint):
  """Current All Open Orders"""

  async def current_all_open_orders(
    self,
    *,
    symbol: str | None = None,
    pair: str | None = None,
    validate: bool | None = None,
  ) -> list[CoinMOpenOrder]:
    """Get all open orders on a symbol or pair. Be careful when calling with neither — it returns every open order on the account.

    Args:
      symbol: Symbol. After the CM/UM migration, an invalid `symbol` returns error -1121 (previously a silent 200 with an empty array).
      pair: Underlying pair.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#current-all-open-orders)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if pair is not None:
      params['pair'] = pair
    _Response = list[CoinMOpenOrder]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/dapi/v1/openOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
