from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMCancelOrderResult(TypedDict):
  """The canceled order."""

  clientOrderId: NotRequired[str]
  """Client order ID."""
  cumQty: NotRequired[str]
  """Cumulative filled quantity, in contracts."""
  executedQty: NotRequired[str]
  """Executed quantity, in contracts."""
  orderId: int
  """Order ID."""
  origQty: NotRequired[str]
  """Original order quantity, in contracts."""
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
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'GTX']]
  """Time in force."""
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


class CancelOrder(RpcEndpoint):
  """Cancel Order"""

  async def cancel_order(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    orig_client_order_id: str | None = None,
    validate: bool | None = None,
  ) -> CoinMCancelOrderResult:
    """Cancel an active order.

    Args:
      symbol: Symbol.
      order_id: Order ID. Either `orderId` or `origClientOrderId` must be sent.
      orig_client_order_id: Client order ID.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#cancel-order)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    _Response = CoinMCancelOrderResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE', '/dapi/v1/order', params=params, validator=_validator, validate=validate
    )
