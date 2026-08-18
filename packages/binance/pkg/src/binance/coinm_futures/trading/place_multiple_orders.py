from json import dumps
from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMBatchNewOrderParams(TypedDict):
  """One order within a batch place request. Same field rules as `new_order`."""

  symbol: str
  """Symbol."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """Position side. `BOTH` for One-way Mode; `LONG` or `SHORT` for Hedge Mode."""
  type: Literal[
    'LIMIT',
    'MARKET',
    'STOP',
    'STOP_MARKET',
    'TAKE_PROFIT',
    'TAKE_PROFIT_MARKET',
    'TRAILING_STOP_MARKET',
  ]
  """Order type. See `notes` — after the CM/UM migration this endpoint rejects the five stop-type values with -4120; only LIMIT and MARKET are currently accepted here."""
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'GTX']]
  """Time in force."""
  reduceOnly: NotRequired[Literal['true', 'false']]
  """Whether the order is reduce-only."""
  quantity: NotRequired[float]
  """Order quantity, in contracts."""
  price: NotRequired[float]
  """Order price."""
  newClientOrderId: NotRequired[str]
  """A unique id among open orders."""
  stopPrice: NotRequired[float]
  """Trigger price."""
  closePosition: NotRequired[Literal['true', 'false']]
  """Close-All."""
  activationPrice: NotRequired[float]
  """Used with TRAILING_STOP_MARKET orders."""
  callbackRate: NotRequired[float]
  """Callback rate for TRAILING_STOP_MARKET orders. Min 0.1, max 4, where 1 means 1% (batch endpoint's documented range differs from the single `new_order` endpoint's 0.1-10 — a venue inconsistency, not a spec error)."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """stopPrice trigger price type."""
  priceProtect: NotRequired[Literal['true', 'false']]
  """Whether the conditional order's trigger is price-protected."""
  newOrderRespType: NotRequired[Literal['ACK', 'RESULT']]
  """Response verbosity."""
  priceMatch: NotRequired[
    Literal[
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
  ]
  """Price match mode. Only available for LIMIT/STOP/TAKE_PROFIT orders; cannot be sent together with `price`."""
  selfTradePreventionMode: NotRequired[
    Literal['NONE', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'EXPIRE_MAKER']
  ]
  """Self-trade prevention mode. Only effective when `timeInForce` is IOC or GTC."""


class CoinMBatchNewOrderSuccess(TypedDict):
  """A successfully-placed order within the batch."""

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
  closePosition: NotRequired[bool]
  """Whether the order closes the whole position (Close-All)."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """Position side."""
  status: Literal['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'EXPIRED']
  """Order status. Documented closed set (COIN-M common-definition doc)."""
  stopPrice: NotRequired[str]
  """Stop trigger price. Ignored when order type is TRAILING_STOP_MARKET."""
  symbol: str
  """Symbol."""
  pair: NotRequired[str]
  """Underlying pair."""
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'GTX']]
  """Time in force."""
  type: Literal[
    'LIMIT',
    'MARKET',
    'STOP',
    'STOP_MARKET',
    'TAKE_PROFIT',
    'TAKE_PROFIT_MARKET',
    'TRAILING_STOP_MARKET',
  ]
  """Order type. See `notes` — after the CM/UM migration this endpoint rejects the five stop-type values with -4120; only LIMIT and MARKET are currently accepted here."""
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
  """Last update time."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """stopPrice trigger price type."""
  priceProtect: NotRequired[bool]
  """Whether the conditional order's trigger is price-protected."""
  priceMatch: NotRequired[str]
  """Price match mode."""
  selfTradePreventionMode: NotRequired[str]
  """Self-trade prevention mode."""


class CoinMBatchOrderError(TypedDict):
  """A batch element that failed."""

  code: int
  """Binance error code for this element."""
  msg: str
  """Error message for this element."""


class PlaceMultipleOrders(RpcEndpoint):
  """Place Multiple Orders"""

  async def place_multiple_orders(
    self,
    *,
    batch_orders: list[CoinMBatchNewOrderParams],
    validate: bool | None = None,
  ) -> list[CoinMBatchNewOrderSuccess | CoinMBatchOrderError]:
    """Place up to 5 orders in one request. Orders are matched concurrently; the response array preserves the request's order.

    Args:
      batch_orders: Order list, max 5 orders. Sent as a JSON-array-valued query parameter, e.g. `batchOrders=[{...}]`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#place-multiple-orders)
    """
    params: dict = {
      'batchOrders': dumps(batch_orders, separators=(',', ':')),
    }
    _Response = list[CoinMBatchNewOrderSuccess | CoinMBatchOrderError]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.authed_request(
      'POST',
      '/dapi/v1/batchOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
