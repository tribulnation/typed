from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class OrderExtendResult(TypedDict):
  """Result of extending the order's validity period."""

  success: NotRequired[bool]
  """Whether the order's validity period was successfully extended by 30 minutes."""


class OrderExtend(RpcEndpoint):
  """Extend a Spot Block Matching order's validity period by adding 30 minutes to the current time."""

  async def order_extend(
    self,
    *,
    order_id: int,
    validate: bool | None = None,
  ) -> OrderExtendResult:
    """Extend a Spot Block Matching order's validity period by adding 30 minutes to the current time.

    Args:
      order_id: Order ID.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-spot-block-matching/api/rest-api/~#order-extend)
    """
    params: dict = {
      'orderId': order_id,
    }
    _Response = OrderExtendResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/block-match/order/extend',
      params=params,
      validator=_validator,
      validate=validate,
    )
