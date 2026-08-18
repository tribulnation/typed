from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CommissionDiscount(TypedDict):
  """Discount applied to standard commissions when paying fees in BNB."""

  enabledForAccount: bool
  """Whether the BNB fee discount is enabled for the account."""
  enabledForSymbol: bool
  """Whether the BNB fee discount is enabled for the symbol."""
  discountAsset: str
  """Asset the discount is denominated in."""
  discount: str
  """Rate the standard commission is reduced by when paying in discountAsset."""


class SorOrderTestEmpty(TypedDict):
  """Empty response when computeCommissionRates is false or omitted."""


class StandardCommissionRates(TypedDict):
  """Standard commission rates on trades from the order."""

  maker: str
  """Maker commission rate."""
  taker: str
  """Taker commission rate."""


class TaxCommissionRates(TypedDict):
  """Tax commission rates for trades from the order."""

  maker: str
  """Maker commission rate."""
  taker: str
  """Taker commission rate."""


class SorOrderTestCommission(TypedDict):
  """Estimated commission rates for the order, returned when computeCommissionRates is true. Unlike spot.trading.order_test's OrderTestCommission, this shape carries no specialCommissionForOrder -- the SOR test endpoint's documented response omits it."""

  standardCommissionForOrder: StandardCommissionRates
  taxCommissionForOrder: TaxCommissionRates
  discount: CommissionDiscount


class SorOrderTest(RpcEndpoint):
  """Test new order using SOR"""

  async def sor_order_test(
    self,
    *,
    symbol: str,
    side: Literal['BUY', 'SELL'],
    type: Literal['LIMIT', 'MARKET'],
    time_in_force: Literal['GTC', 'IOC', 'FOK'] | None = None,
    quantity: str,
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
    compute_commission_rates: bool | None = None,
    validate: bool | None = None,
  ) -> SorOrderTestEmpty | SorOrderTestCommission:
    """Test new order creation and signature/recvWindow using smart order routing (SOR). Validates the order but does not send it into the matching engine. Accepts every parameter POST /api/v3/sor/order does, plus computeCommissionRates. Only LIMIT and MARKET order types are supported; quoteOrderQty is not supported.

    Args:
      symbol: Trading pair symbol.
      side: Order side.
      type: Order type. Only LIMIT and MARKET are supported by SOR.
      time_in_force: Time in force. Required for LIMIT orders.
      quantity: Order quantity, in the base asset. quoteOrderQty is not supported by SOR.
      price: Order price. Required for LIMIT orders.
      new_client_order_id: Caller-supplied id for the order. Automatically generated if not sent. An order sharing a newClientOrderId with an existing one is only accepted once the existing order has filled.
      strategy_id: Id labeling the order strategy this order is part of.
      strategy_type: Type labeling the order strategy this order is part of. Cannot be less than 1000000.
      iceberg_qty: Quantity per leg of an iceberg order. Usable with LIMIT orders; requires timeInForce GTC.
      new_order_resp_type: Response shape to return. Defaults to FULL.
      self_trade_prevention_mode: Self-trade prevention mode. The allowed values depend on the symbol's configuration.
      compute_commission_rates: Return the commission rates that would apply to the order, at 20x the weight. Default: false.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
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
    if compute_commission_rates is not None:
      params['computeCommissionRates'] = compute_commission_rates
    _Response = SorOrderTestEmpty | SorOrderTestCommission
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.authed_request(
      'POST',
      '/api/v3/sor/order/test',
      params=params,
      validator=_validator,
      validate=validate,
    )
