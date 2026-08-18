from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmCancelMarginAccountOrder(TypedDict):
  """Cancel Margin Account Order."""

  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  origClientOrderId: NotRequired[str]
  """Orig Client Order ID."""
  clientOrderId: NotRequired[str]
  """Client Order ID."""
  price: NotRequired[str]
  """Price."""
  origQty: NotRequired[str]
  """Orig Qty."""
  executedQty: NotRequired[str]
  """Executed Qty."""
  cummulativeQuoteQty: NotRequired[str]
  """Cummulative Quote Qty."""
  status: NotRequired[str]
  """Enum：completed，processing."""
  timeInForce: NotRequired[str]
  """Time In Force."""
  type: NotRequired[str]
  """Normal order type after trigger if appliable."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Side."""


class CancelMarginOrder(RpcEndpoint):
  """Cancel Margin Account Order"""

  async def cancel_margin_order(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    orig_client_order_id: str | None = None,
    new_client_order_id: str | None = None,
    validate: bool | None = None,
  ) -> PmCancelMarginAccountOrder:
    """Cancel Margin Account Order.

    Args:
      symbol: Symbol.
      order_id: Order id to act on.
      orig_client_order_id: Caller-supplied id of the order to act on, as given on placement.
      new_client_order_id: Used to uniquely identify this cancel request.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#cancel-margin-account-order)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    _Response = PmCancelMarginAccountOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/papi/v1/margin/order',
      params=params,
      validator=_validator,
      validate=validate,
    )
