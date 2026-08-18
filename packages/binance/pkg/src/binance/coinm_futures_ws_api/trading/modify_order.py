from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class CoinMWsModifiedOrder(TypedDict):
  """The modified order."""

  clientOrderId: NotRequired[str]
  """Client order id."""
  cumQty: NotRequired[str]
  """Cumulative filled quantity, in contracts."""
  executedQty: NotRequired[str]
  """Executed quantity, in contracts."""
  orderId: int
  """Order id."""
  origQty: NotRequired[str]
  """Original order quantity, in contracts."""
  price: NotRequired[str]
  """Order price."""
  reduceOnly: NotRequired[bool]
  """Whether the order is reduce-only."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """Position side."""
  status: Literal['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'EXPIRED']
  """Order status."""
  stopPrice: NotRequired[str]
  """Stop trigger price. Ignored when order type is TRAILING_STOP_MARKET."""
  closePosition: NotRequired[bool]
  """Whether the order closes the whole position (Close-All)."""
  symbol: str
  """Trading symbol."""
  pair: NotRequired[str]
  """Underlying pair."""
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
  """Order type. See notes -- after the CM migration this endpoint rejects the five stop-type values with -4120; only LIMIT and MARKET are currently accepted."""
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
  activatePrice: NotRequired[str]
  """Activation price. Only returned for TRAILING_STOP_MARKET orders."""
  priceRate: NotRequired[str]
  """Callback rate. Only returned for TRAILING_STOP_MARKET orders."""
  updateTime: NotRequired[int]
  """Last update time, milliseconds since epoch."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """stopPrice trigger price type."""
  priceProtect: NotRequired[bool]
  """Whether the conditional order's trigger is price-protected."""
  priceMatch: NotRequired[str]
  """Price match mode."""
  selfTradePreventionMode: NotRequired[str]
  """Self-trade prevention mode."""
  modifyId: NotRequired[int]
  """User-supplied modification identifier, echoed back if it was sent on the request."""


class ModifyOrder(WsRpcEndpoint):
  """Modify an existing LIMIT order's price and/or quantity. Currently only LIMIT order modification is supported; the order is re-queued in the match engine."""

  async def modify_order(
    self,
    *,
    symbol: str,
    side: Literal['BUY', 'SELL'],
    order_id: int | None = None,
    orig_client_order_id: str | None = None,
    quantity: str,
    price: str,
    price_match: Literal[
      'NONE',
      'OPPONENT',
      'OPPONENT_5',
      'OPPONENT_10',
      'OPPONENT_20',
      'QUEUE',
      'QUEUE_5',
      'QUEUE_10',
      'QUEUE_20',
    ]
    | None = None,
    modify_id: int | None = None,
    validate: bool | None = None,
  ) -> CoinMWsModifiedOrder:
    """Modify an existing LIMIT order's price and/or quantity. Currently only LIMIT order modification is supported; the order is re-queued in the match engine.

    Args:
      symbol: Symbol.
      side: Order side.
      order_id: Order id. Either orderId or origClientOrderId must be sent; orderId prevails if both are.
      orig_client_order_id: Client order id.
      quantity: New order quantity, in contracts. Required (must be sent together with price) after the CM migration.
      price: New order price. Required (must be sent together with quantity) after the CM migration.
      price_match: Price match mode. Only available for LIMIT/STOP/TAKE_PROFIT orders; cannot be sent together with price.
      modify_id: User-defined modification identifier, echoed back as-is in the response if sent. Not validated for uniqueness.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-api/trade#modify-order)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'quantity': quantity,
      'price': price,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    if price_match is not None:
      params['priceMatch'] = price_match
    if modify_id is not None:
      params['modifyId'] = modify_id
    _Response = CoinMWsModifiedOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'order.modify', params=params, validator=_validator, validate=validate
    )
