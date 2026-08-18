from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class OrderAck(TypedDict):
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


class OrderFill(TypedDict):
  """One trade that filled part or all of this order."""

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


class OrderResult(TypedDict):
  """Order acknowledgement with fill/status detail, returned when newOrderRespType is RESULT."""

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
  """Price at which the algorithmic order triggers. Present for STOP_LOSS, TAKE_PROFIT, STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT orders."""
  strategyId: NotRequired[int]
  """Id labeling the order strategy this order is part of. Present when strategyId was sent in the request."""
  strategyType: NotRequired[int]
  """Type labeling the order strategy this order is part of. Present when strategyType was sent in the request."""
  trailingDelta: NotRequired[int]
  """Delta price change required before order activation. Present for trailing stop orders."""
  trailingTime: NotRequired[Timestamp]
  """Time the trailing order became active and started tracking price changes. Present only for trailing stop orders."""
  usedSor: NotRequired[bool]
  """Whether the order used smart order routing (SOR). Present when the order was placed using SOR."""
  workingFloor: NotRequired[Literal['EXCHANGE', 'SOR']]
  """Whether the order is being filled by SOR or by the order book it was submitted to. Present when the order was placed using SOR."""
  pegPriceType: NotRequired[Literal['PRIMARY_PEG', 'MARKET_PEG']]
  """Peg reference type. Present only for pegged orders."""
  pegOffsetType: NotRequired[Literal['PRICE_LEVEL']]
  """Peg offset type. Present only for pegged orders that requested one."""
  pegOffsetValue: NotRequired[int]
  """Peg offset value. Present only for pegged orders that requested one."""
  peggedPrice: NotRequired[str]
  """Current price the order is pegged at. Present only for pegged orders, once determined."""
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


class OrderFull(TypedDict):
  """Full order acknowledgement with fill detail, returned when newOrderRespType is FULL."""

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
  """Price at which the algorithmic order triggers. Present for STOP_LOSS, TAKE_PROFIT, STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT orders."""
  strategyId: NotRequired[int]
  """Id labeling the order strategy this order is part of. Present when strategyId was sent in the request."""
  strategyType: NotRequired[int]
  """Type labeling the order strategy this order is part of. Present when strategyType was sent in the request."""
  trailingDelta: NotRequired[int]
  """Delta price change required before order activation. Present for trailing stop orders."""
  trailingTime: NotRequired[Timestamp]
  """Time the trailing order became active and started tracking price changes. Present only for trailing stop orders."""
  usedSor: NotRequired[bool]
  """Whether the order used smart order routing (SOR). Present when the order was placed using SOR."""
  workingFloor: NotRequired[Literal['EXCHANGE', 'SOR']]
  """Whether the order is being filled by SOR or by the order book it was submitted to. Present when the order was placed using SOR."""
  pegPriceType: NotRequired[Literal['PRIMARY_PEG', 'MARKET_PEG']]
  """Peg reference type. Present only for pegged orders."""
  pegOffsetType: NotRequired[Literal['PRICE_LEVEL']]
  """Peg offset type. Present only for pegged orders that requested one."""
  pegOffsetValue: NotRequired[int]
  """Peg offset value. Present only for pegged orders that requested one."""
  peggedPrice: NotRequired[str]
  """Current price the order is pegged at. Present only for pegged orders, once determined."""
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
  fills: list[OrderFill]
  """Trades that filled this order."""


class Order(RpcEndpoint):
  """New order"""

  async def order(
    self,
    *,
    symbol: str,
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
    time_in_force: Literal['GTC', 'IOC', 'FOK'] | None = None,
    quantity: str | None = None,
    quote_order_qty: str | None = None,
    price: str | None = None,
    new_client_order_id: str | None = None,
    strategy_id: int | None = None,
    strategy_type: int | None = None,
    iceberg_qty: str | None = None,
    new_order_resp_type: Literal['ACK', 'RESULT', 'FULL'] | None = None,
    self_trade_prevention_mode: Literal[
      'NONE', 'EXPIRE_MAKER', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'DECREMENT', 'TRANSFER'
    ]
    | None = None,
    stop_price: str | None = None,
    trailing_delta: int | None = None,
    peg_price_type: Literal['PRIMARY_PEG', 'MARKET_PEG'] | None = None,
    peg_offset_value: int | None = None,
    peg_offset_type: Literal['PRICE_LEVEL'] | None = None,
    validate: bool | None = None,
  ) -> OrderAck | OrderResult | OrderFull:
    """Place a new spot order. Additional parameters become mandatory depending on type: LIMIT requires timeInForce, quantity and price; MARKET requires quantity or quoteOrderQty; STOP_LOSS and TAKE_PROFIT require quantity and either stopPrice or trailingDelta; STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT require timeInForce, quantity, price and either stopPrice or trailingDelta; LIMIT_MAKER requires quantity and price. Pegged-order parameters (pegPriceType, pegOffsetType, pegOffsetValue) are usable with LIMIT, LIMIT_MAKER, STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT orders; see upstream.md for the full type-conditional parameter table and Pegged Orders notes.

    Args:
      symbol: Trading pair symbol.
      side: Order side.
      type: Order type.
      time_in_force: Time in force. Required for LIMIT, STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT orders.
      quantity: Order quantity, in the base asset.
      quote_order_qty: Order quantity, in the quote asset. Usable in place of quantity for MARKET orders.
      price: Order price. Required for LIMIT, STOP_LOSS_LIMIT, TAKE_PROFIT_LIMIT and LIMIT_MAKER orders, unless pegPriceType is set.
      new_client_order_id: Caller-supplied id for the order. Automatically generated if not sent. An order sharing a newClientOrderId with an existing one is only accepted once the existing order has filled.
      strategy_id: Id labeling the order strategy this order is part of.
      strategy_type: Type labeling the order strategy this order is part of. Cannot be less than 1000000.
      iceberg_qty: Quantity per leg of an iceberg order. Usable with LIMIT, STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT orders; any order carrying it must set timeInForce to GTC.
      new_order_resp_type: Response shape to return. MARKET and LIMIT orders default to FULL; all other order types default to ACK.
      self_trade_prevention_mode: Self-trade prevention mode. The allowed values depend on the symbol's configuration.
      stop_price: Price at which a STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT or TAKE_PROFIT_LIMIT order triggers.
      trailing_delta: Delta for a trailing stop order, combinable with stopPrice.
      peg_price_type: Peg reference for a pegged order: the best same-side price (PRIMARY_PEG) or the best opposite-side price (MARKET_PEG). Usable with LIMIT, LIMIT_MAKER, STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT orders; makes price optional when set.
      peg_offset_value: Price level offset from the peg reference, up to 100. Must be sent together with pegOffsetType.
      peg_offset_type: Peg offset type. Only PRICE_LEVEL is supported. Must be sent together with pegOffsetValue.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'type': type,
    }
    if time_in_force is not None:
      params['timeInForce'] = time_in_force
    if quantity is not None:
      params['quantity'] = quantity
    if quote_order_qty is not None:
      params['quoteOrderQty'] = quote_order_qty
    if price is not None:
      params['price'] = price
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    if strategy_id is not None:
      params['strategyId'] = strategy_id
    if strategy_type is not None:
      params['strategyType'] = strategy_type
    if iceberg_qty is not None:
      params['icebergQty'] = iceberg_qty
    if new_order_resp_type is not None:
      params['newOrderRespType'] = new_order_resp_type
    if self_trade_prevention_mode is not None:
      params['selfTradePreventionMode'] = self_trade_prevention_mode
    if stop_price is not None:
      params['stopPrice'] = stop_price
    if trailing_delta is not None:
      params['trailingDelta'] = trailing_delta
    if peg_price_type is not None:
      params['pegPriceType'] = peg_price_type
    if peg_offset_value is not None:
      params['pegOffsetValue'] = peg_offset_value
    if peg_offset_type is not None:
      params['pegOffsetType'] = peg_offset_type
    _Response = OrderAck | OrderResult | OrderFull
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.authed_request(
      'POST', '/api/v3/order', params=params, validator=_validator, validate=validate
    )
