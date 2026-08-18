from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class AlgoOrderAck(TypedDict):
  """Acknowledgement that an Algo order was accepted for processing."""

  clientAlgoId: str
  """Client-supplied (or server-generated) unique Algo order identifier."""
  success: bool
  """Whether the order was accepted. Does not mean the order will be executed — check `openOrders`/`historicalOrders` for the real status."""
  code: int
  """Response code. `0` on success."""
  msg: str
  """Response message. `"OK"` on success."""


class NewOrderTwap(RpcEndpoint):
  """Time-Weighted Average Price (TWAP) New Order (TRADE)"""

  async def new_order_twap(
    self,
    *,
    symbol: str,
    side: Literal['SELL', 'BUY'],
    quantity: float,
    duration: int,
    client_algo_id: str | None = None,
    limit_price: float | None = None,
    validate: bool | None = None,
  ) -> AlgoOrderAck:
    """Place a new spot TWAP order with the Algo service. Disperses a large order into smaller child orders executed at regular intervals over `duration` to approximate the time-weighted average price. Maximum 20 open Algo orders allowed per account. Minimum notional: 1,000 USDT equivalent; maximum: 100,000 USDT equivalent (per developers.binance.com; the swagger response confirms shape but not these limits).

    Args:
      symbol: Trading symbol, e.g. BNBUSDT.
      side: Order side.
      quantity: Quantity of the base asset to trade.
      duration: TWAP duration in seconds. Range [300, 86400] (5 minutes to 24 hours); below 300 defaults to 300, above 86400 defaults to 86400.
      client_algo_id: Unique 32-character client identifier for this Algo order. Auto-generated if omitted.
      limit_price: Limit price for child orders. Market price is used if omitted.

    References:
      - [Official docs](https://developers.binance.com/docs/algo/spot-algo/Time-Weighted-Average-Price-New-Order)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'quantity': quantity,
      'duration': duration,
    }
    if client_algo_id is not None:
      params['clientAlgoId'] = client_algo_id
    if limit_price is not None:
      params['limitPrice'] = limit_price
    _Response = AlgoOrderAck
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/algo/spot/newOrderTwap',
      params=params,
      validator=_validator,
      validate=validate,
    )
