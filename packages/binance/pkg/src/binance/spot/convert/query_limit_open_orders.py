from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class ConvertLimitOpenOrder(TypedDict):
  """One open Convert limit order."""

  quoteId: NotRequired[str]
  """Quote identifier backing the order."""
  orderId: NotRequired[int]
  """Order identifier."""
  orderStatus: NotRequired[str]
  """Current order status."""
  fromAsset: NotRequired[str]
  """Asset debited when the order fills."""
  fromAmount: NotRequired[str]
  """Amount debited when the order fills."""
  toAsset: NotRequired[str]
  """Asset credited when the order fills."""
  toAmount: NotRequired[str]
  """Amount credited when the order fills."""
  ratio: NotRequired[str]
  """Limit price ratio, `toAmount` / `fromAmount`."""
  inverseRatio: NotRequired[str]
  """Inverse limit price ratio, `fromAmount` / `toAmount`."""
  createTime: NotRequired[int]
  """Millisecond epoch order creation timestamp."""
  expiredTimestamp: NotRequired[int]
  """Millisecond epoch timestamp the order expires at."""


class ConvertLimitOpenOrders(TypedDict):
  """This account's currently open Convert limit orders."""

  list: NotRequired[list[ConvertLimitOpenOrder]]
  """Open limit orders."""


class QueryLimitOpenOrders(RpcEndpoint):
  """Query this account's currently open Convert limit orders."""

  async def query_limit_open_orders(
    self,
    *,
    validate: bool | None = None,
  ) -> ConvertLimitOpenOrders:
    """Query this account's currently open Convert limit orders.

    References:
      - [Official docs](https://developers.binance.com/docs/convert/trade)
    """
    _Response = ConvertLimitOpenOrders
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/convert/limit/queryOpenOrders',
      validator=_validator,
      validate=validate,
    )
