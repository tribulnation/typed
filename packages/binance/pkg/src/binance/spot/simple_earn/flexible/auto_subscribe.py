from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FlexibleAutoSubscribeResult(TypedDict):
  """Result of changing a flexible product's auto-subscribe setting."""

  success: NotRequired[bool]
  """Whether the setting was updated successfully."""


class AutoSubscribe(RpcEndpoint):
  """Set whether future rewards from a Simple Earn flexible product auto-subscribe back into the same product."""

  async def __call__(
    self,
    *,
    product_id: str,
    auto_subscribe: bool,
    validate: bool | None = None,
  ) -> FlexibleAutoSubscribeResult:
    """Set whether future rewards from a Simple Earn flexible product auto-subscribe back into the same product.

    Args:
      product_id: Flexible product identifier to change the auto-subscribe setting for.
      auto_subscribe: Whether future rewards should auto-subscribe back into this product.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#set-flexible-auto-subscribe)
    """
    params: dict = {
      'productId': product_id,
      'autoSubscribe': auto_subscribe,
    }
    _Response = FlexibleAutoSubscribeResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/simple-earn/flexible/setAutoSubscribe',
      params=params,
      validator=_validator,
      validate=validate,
    )
