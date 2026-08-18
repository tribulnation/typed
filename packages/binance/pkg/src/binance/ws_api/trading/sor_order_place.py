from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class SorOrderAck(TypedDict):
  """Minimal order acknowledgement, returned when newOrderRespType is ACK."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  orderListId: int
  """Id of the order list this order belongs to, or -1 if it is not part of one."""
  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""
  transactTime: Timestamp
  """Time the order was processed."""


class SorOrderFill(TypedDict):
  """One trade that filled part or all of this order, via SOR."""

  price: str
  """Fill price."""
  qty: str
  """Filled quantity."""
  commission: str
  """Commission charged on the fill."""
  commissionAsset: str
  """Asset the commission was charged in."""
  tradeId: int
  """Trade id of the fill."""
  matchType: str
  """Type of match that produced this fill, e.g. ONE_PARTY_TRADE_REPORT. Not a documented closed set (absent from enums.md and web-socket-api.md's prose), so left bare per authoring.md rule 2."""
  allocId: int
  """Allocation id of the fill."""


class SorOrderResult(TypedDict):
  """Order acknowledgement with fill/status detail, returned when newOrderRespType is RESULT. workingFloor and usedSor are always present, since every order placed through this endpoint is routed by SOR."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  orderListId: int
  """Id of the order list this order belongs to, or -1 if it is not part of one."""
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
  origQuoteOrderQty: str
  """Original quoteOrderQty, or "0" when quoteOrderQty was not used."""
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
  workingTime: Timestamp
  """Time the order started working on the order book."""
  selfTradePreventionMode: Literal[
    'NONE', 'EXPIRE_MAKER', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'DECREMENT', 'TRANSFER'
  ]
  """Self-trade prevention mode in effect for the order."""
  icebergQty: NotRequired[str]
  """Quantity for the iceberg order. Present only when icebergQty was sent in the request."""
  preventedMatchId: NotRequired[int]
  """Id of a prevented match, usable together with symbol to query it. Present only when the order expired due to self-trade prevention."""
  preventedQuantity: NotRequired[str]
  """Order quantity that expired due to self-trade prevention. Present only when the order expired due to self-trade prevention."""
  stopPrice: NotRequired[str]
  """Price at which the algorithmic order triggers. Not applicable to sor.order.place, which only supports LIMIT and MARKET, but retained for shape parity with the general order response."""
  strategyId: NotRequired[int]
  """Id labeling the order strategy this order is part of. Present when strategyId was sent in the request."""
  strategyType: NotRequired[int]
  """Type labeling the order strategy this order is part of. Present when strategyType was sent in the request."""
  trailingDelta: NotRequired[int]
  """Delta price change required before order activation. Not applicable to sor.order.place, which only supports LIMIT and MARKET, but retained for shape parity with the general order response."""
  trailingTime: NotRequired[Timestamp]
  """Time the trailing order became active and started tracking price changes. Not applicable to sor.order.place, which only supports LIMIT and MARKET, but retained for shape parity with the general order response."""
  usedSor: bool
  """Whether the order used smart order routing (SOR). Always true for orders placed through this endpoint."""
  workingFloor: Literal['EXCHANGE', 'SOR']
  """Whether the order is being filled by SOR or by the order book it was submitted to."""
  pegPriceType: NotRequired[Literal['PRIMARY_PEG', 'MARKET_PEG']]
  """Peg reference type. Not applicable to sor.order.place, which accepts no peg parameters, but retained for shape parity with the general order response."""
  pegOffsetType: NotRequired[Literal['PRICE_LEVEL']]
  """Peg offset type. Not applicable to sor.order.place, which accepts no peg parameters, but retained for shape parity with the general order response."""
  pegOffsetValue: NotRequired[int]
  """Peg offset value. Not applicable to sor.order.place, which accepts no peg parameters, but retained for shape parity with the general order response."""
  peggedPrice: NotRequired[str]
  """Current price the order is pegged at. Not applicable to sor.order.place, which accepts no peg parameters, but retained for shape parity with the general order response."""
  expiryReason: NotRequired[
    Literal[
      'NONE',
      'REJECTED',
      'EXCHANGE_CANCELED',
      'OCO_TRIGGER',
      'OTO_PHASE_ONE_EXPIRED',
      'UNFILLED_IOC_QUANTITY_EXPIRED',
      'UNFILLED_FOK_ORDER_EXPIRED',
      'INSUFFICIENT_LIQUIDITY',
      'EXECUTION_RULE_PRICE_RANGE_EXCEEDED',
    ]
  ]
  """Cause of the order's expiration. Present when the order has expired."""


class SorOrderFull(TypedDict):
  """Full order acknowledgement with fill detail, returned when newOrderRespType is FULL. workingFloor and usedSor are always present, since every order placed through this endpoint is routed by SOR."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  orderListId: int
  """Id of the order list this order belongs to, or -1 if it is not part of one."""
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
  origQuoteOrderQty: str
  """Original quoteOrderQty, or "0" when quoteOrderQty was not used."""
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
  workingTime: Timestamp
  """Time the order started working on the order book."""
  selfTradePreventionMode: Literal[
    'NONE', 'EXPIRE_MAKER', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'DECREMENT', 'TRANSFER'
  ]
  """Self-trade prevention mode in effect for the order."""
  icebergQty: NotRequired[str]
  """Quantity for the iceberg order. Present only when icebergQty was sent in the request."""
  preventedMatchId: NotRequired[int]
  """Id of a prevented match, usable together with symbol to query it. Present only when the order expired due to self-trade prevention."""
  preventedQuantity: NotRequired[str]
  """Order quantity that expired due to self-trade prevention. Present only when the order expired due to self-trade prevention."""
  stopPrice: NotRequired[str]
  """Price at which the algorithmic order triggers. Not applicable to sor.order.place, which only supports LIMIT and MARKET, but retained for shape parity with the general order response."""
  strategyId: NotRequired[int]
  """Id labeling the order strategy this order is part of. Present when strategyId was sent in the request."""
  strategyType: NotRequired[int]
  """Type labeling the order strategy this order is part of. Present when strategyType was sent in the request."""
  trailingDelta: NotRequired[int]
  """Delta price change required before order activation. Not applicable to sor.order.place, which only supports LIMIT and MARKET, but retained for shape parity with the general order response."""
  trailingTime: NotRequired[Timestamp]
  """Time the trailing order became active and started tracking price changes. Not applicable to sor.order.place, which only supports LIMIT and MARKET, but retained for shape parity with the general order response."""
  usedSor: bool
  """Whether the order used smart order routing (SOR). Always true for orders placed through this endpoint."""
  workingFloor: Literal['EXCHANGE', 'SOR']
  """Whether the order is being filled by SOR or by the order book it was submitted to."""
  pegPriceType: NotRequired[Literal['PRIMARY_PEG', 'MARKET_PEG']]
  """Peg reference type. Not applicable to sor.order.place, which accepts no peg parameters, but retained for shape parity with the general order response."""
  pegOffsetType: NotRequired[Literal['PRICE_LEVEL']]
  """Peg offset type. Not applicable to sor.order.place, which accepts no peg parameters, but retained for shape parity with the general order response."""
  pegOffsetValue: NotRequired[int]
  """Peg offset value. Not applicable to sor.order.place, which accepts no peg parameters, but retained for shape parity with the general order response."""
  peggedPrice: NotRequired[str]
  """Current price the order is pegged at. Not applicable to sor.order.place, which accepts no peg parameters, but retained for shape parity with the general order response."""
  expiryReason: NotRequired[
    Literal[
      'NONE',
      'REJECTED',
      'EXCHANGE_CANCELED',
      'OCO_TRIGGER',
      'OTO_PHASE_ONE_EXPIRED',
      'UNFILLED_IOC_QUANTITY_EXPIRED',
      'UNFILLED_FOK_ORDER_EXPIRED',
      'INSUFFICIENT_LIQUIDITY',
      'EXECUTION_RULE_PRICE_RANGE_EXCEEDED',
    ]
  ]
  """Cause of the order's expiration. Present when the order has expired."""
  fills: list[SorOrderFill]
  """Trades that filled this order. SOR orders may fill against several counterparty order books, so fills can carry different allocId values."""


class SorOrderPlace(WsRpcEndpoint):
  """New order using SOR"""

  async def sor_order_place(
    self,
    *,
    symbol: str,
    side: Literal['BUY', 'SELL'],
    type: Literal['LIMIT', 'MARKET'],
    time_in_force: Literal['GTC', 'IOC', 'FOK'] | None = None,
    price: str | None = None,
    quantity: str,
    new_client_order_id: str | None = None,
    new_order_resp_type: Literal['ACK', 'RESULT', 'FULL'] | None = None,
    iceberg_qty: str | None = None,
    strategy_id: int | None = None,
    strategy_type: int | None = None,
    self_trade_prevention_mode: Literal[
      'NONE', 'EXPIRE_MAKER', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'DECREMENT', 'TRANSFER'
    ]
    | None = None,
    validate: bool | None = None,
  ) -> list[SorOrderAck | SorOrderResult | SorOrderFull]:
    """Place a new spot order using smart order routing (SOR), which can fill against liquidity from multiple order books. Only LIMIT and MARKET order types are supported; quoteOrderQty is not supported (quantity is always required). This adds 1 order to the EXCHANGE_MAX_ORDERS filter and the MAX_NUM_ORDERS filter.

    Args:
      symbol: Trading pair symbol.
      side: Order side.
      type: Order type. sor.order.place only supports LIMIT and MARKET.
      time_in_force: Time in force. Applicable only to LIMIT orders.
      price: Order price. Applicable only to LIMIT orders.
      quantity: Order quantity, in the base asset. quoteOrderQty is not supported by SOR.
      new_client_order_id: Caller-supplied id for the order. Automatically generated if not sent. An order sharing a newClientOrderId with an existing one is only accepted once the existing order has filled.
      new_order_resp_type: Response shape to return. MARKET and LIMIT orders use FULL by default.
      iceberg_qty: Quantity per leg of an iceberg order.
      strategy_id: Id labeling the order strategy this order is part of.
      strategy_type: Type labeling the order strategy this order is part of. Cannot be less than 1000000.
      self_trade_prevention_mode: Self-trade prevention mode. The allowed values depend on the symbol's configuration.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#place-new-order-using-sor-trade)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'type': type,
      'quantity': quantity,
    }
    if time_in_force is not None:
      params['timeInForce'] = time_in_force
    if price is not None:
      params['price'] = price
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    if new_order_resp_type is not None:
      params['newOrderRespType'] = new_order_resp_type
    if iceberg_qty is not None:
      params['icebergQty'] = iceberg_qty
    if strategy_id is not None:
      params['strategyId'] = strategy_id
    if strategy_type is not None:
      params['strategyType'] = strategy_type
    if self_trade_prevention_mode is not None:
      params['selfTradePreventionMode'] = self_trade_prevention_mode
    _Response = list[SorOrderAck | SorOrderResult | SorOrderFull]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.authed_request(
      'sor.order.place', params=params, validator=_validator, validate=validate
    )
