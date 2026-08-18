from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class MarginOrderAck(TypedDict):
  """Minimal order acknowledgement, returned when newOrderRespType is ACK."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""
  isIsolated: bool
  """Whether the order belongs to an isolated margin account."""
  transactTime: Timestamp
  """Time the order was processed."""


class MarginOrderFill(TypedDict):
  """One trade that filled part or all of this order."""

  price: str
  """Fill price."""
  qty: str
  """Filled quantity."""
  commission: str
  """Commission charged on the fill."""
  commissionAsset: str
  """Asset the commission was charged in."""


class MarginOrderResult(TypedDict):
  """Order acknowledgement with fill/status detail, returned when newOrderRespType is RESULT."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""
  transactTime: Timestamp
  """Time the order was processed."""
  price: str
  """Order price."""
  origQty: str
  """Original order quantity."""
  executedQty: str
  """Cumulative filled quantity."""
  cummulativeQuoteQty: str
  """Cumulative quote asset transacted quantity."""
  status: Literal[
    'NEW',
    'PENDING_NEW',
    'PARTIALLY_FILLED',
    'FILLED',
    'CANCELED',
    'PENDING_CANCEL',
    'REJECTED',
    'EXPIRED',
    'EXPIRED_IN_MATCH',
  ]
  """Order status."""
  timeInForce: Literal['GTC', 'IOC', 'FOK']
  """Time in force."""
  type: Literal[
    'LIMIT',
    'MARKET',
    'STOP_LOSS',
    'STOP_LOSS_LIMIT',
    'TAKE_PROFIT',
    'TAKE_PROFIT_LIMIT',
    'LIMIT_MAKER',
  ]
  """Order type."""
  isIsolated: bool
  """Whether the order belongs to an isolated margin account."""
  side: Literal['BUY', 'SELL']
  """Order side."""


class MarginOrderFull(TypedDict):
  """Full order acknowledgement with fill detail, returned when newOrderRespType is FULL."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""
  transactTime: Timestamp
  """Time the order was processed."""
  price: str
  """Order price."""
  origQty: str
  """Original order quantity."""
  executedQty: str
  """Cumulative filled quantity."""
  cummulativeQuoteQty: str
  """Cumulative quote asset transacted quantity."""
  status: Literal[
    'NEW',
    'PENDING_NEW',
    'PARTIALLY_FILLED',
    'FILLED',
    'CANCELED',
    'PENDING_CANCEL',
    'REJECTED',
    'EXPIRED',
    'EXPIRED_IN_MATCH',
  ]
  """Order status."""
  timeInForce: Literal['GTC', 'IOC', 'FOK']
  """Time in force."""
  type: Literal[
    'LIMIT',
    'MARKET',
    'STOP_LOSS',
    'STOP_LOSS_LIMIT',
    'TAKE_PROFIT',
    'TAKE_PROFIT_LIMIT',
    'LIMIT_MAKER',
  ]
  """Order type."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  marginBuyBorrowAmount: NotRequired[float]
  """Amount borrowed to fund the order. Present only when the order triggered a margin borrow."""
  marginBuyBorrowAsset: NotRequired[str]
  """Asset borrowed to fund the order. Present only when the order triggered a margin borrow."""
  isIsolated: bool
  """Whether the order belongs to an isolated margin account."""
  fills: list[MarginOrderFill]
  """Trades that filled this order."""


class NewOrder(RpcEndpoint):
  """Place a new order for a margin account (crossed by default, or a specific isolated symbol when isIsolated is TRUE)."""

  async def new_order(
    self,
    *,
    symbol: str,
    is_isolated: Literal['TRUE', 'FALSE'] | None = None,
    side: Literal['BUY', 'SELL'],
    type: Literal[
      'LIMIT',
      'MARKET',
      'STOP_LOSS',
      'STOP_LOSS_LIMIT',
      'TAKE_PROFIT',
      'TAKE_PROFIT_LIMIT',
      'LIMIT_MAKER',
    ],
    quantity: float | None = None,
    quote_order_qty: float | None = None,
    price: float | None = None,
    stop_price: float | None = None,
    new_client_order_id: str | None = None,
    iceberg_qty: float | None = None,
    new_order_resp_type: Literal['ACK', 'RESULT', 'FULL'] | None = None,
    side_effect_type: Literal[
      'NO_SIDE_EFFECT', 'MARGIN_BUY', 'AUTO_REPAY', 'AUTO_BORROW_REPAY'
    ]
    | None = None,
    time_in_force: Literal['GTC', 'IOC', 'FOK'] | None = None,
    auto_repay_at_cancel: bool,
    self_trade_prevention_mode: Literal[
      'EXPIRE_TAKER', 'EXPIRE_MAKER', 'EXPIRE_BOTH', 'NONE'
    ]
    | None = None,
    validate: bool | None = None,
  ) -> MarginOrderAck | MarginOrderResult | MarginOrderFull:
    """Place a new order for a margin account (crossed by default, or a specific isolated symbol when isIsolated is TRUE).

    Args:
      symbol: Trading pair symbol, e.g. BNBUSDT.
      is_isolated: Margin account type for this order: isolated when TRUE, crossed (default) when FALSE.
      side: Order side.
      type: Order type.
      quantity: Order quantity, in the base asset. Required unless quoteOrderQty is used for a MARKET order.
      quote_order_qty: Order quantity, in the quote asset. Usable in place of quantity for MARKET orders.
      price: Order price. Required for LIMIT, STOP_LOSS_LIMIT, TAKE_PROFIT_LIMIT and LIMIT_MAKER orders.
      stop_price: Price at which the order triggers. Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT and TAKE_PROFIT_LIMIT orders.
      new_client_order_id: Arbitrary unique id among open orders. Automatically generated if not sent.
      iceberg_qty: Quantity per leg of an iceberg order. Usable with LIMIT, STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT orders; any order carrying it must set timeInForce to GTC.
      new_order_resp_type: Response shape to return. MARKET and LIMIT orders default to FULL; all other order types default to ACK.
      side_effect_type: Margin borrow/repay side effect of this order. Defaults to NO_SIDE_EFFECT.
      time_in_force: Time in force. Required for LIMIT, STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT orders.
      auto_repay_at_cancel: Only relevant when sideEffectType is MARGIN_BUY or AUTO_BORROW_REPAY: whether the debt generated by the order should be repaid automatically once the order is canceled.
      self_trade_prevention_mode: Self-trade prevention mode. The allowed values depend on the symbol's configuration.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-new-order)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'type': type,
      'autoRepayAtCancel': auto_repay_at_cancel,
    }
    if is_isolated is not None:
      params['isIsolated'] = is_isolated
    if quantity is not None:
      params['quantity'] = quantity
    if quote_order_qty is not None:
      params['quoteOrderQty'] = quote_order_qty
    if price is not None:
      params['price'] = price
    if stop_price is not None:
      params['stopPrice'] = stop_price
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    if iceberg_qty is not None:
      params['icebergQty'] = iceberg_qty
    if new_order_resp_type is not None:
      params['newOrderRespType'] = new_order_resp_type
    if side_effect_type is not None:
      params['sideEffectType'] = side_effect_type
    if time_in_force is not None:
      params['timeInForce'] = time_in_force
    if self_trade_prevention_mode is not None:
      params['selfTradePreventionMode'] = self_trade_prevention_mode
    _Response = MarginOrderAck | MarginOrderResult | MarginOrderFull
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.authed_request(
      'POST',
      '/sapi/v1/margin/order',
      params=params,
      validator=_validator,
      validate=validate,
    )
