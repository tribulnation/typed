from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LockedAutoSubscribeResult(TypedDict):
  """Result of changing a locked position's auto-subscribe setting."""

  success: NotRequired[bool]
  """Whether the setting was updated successfully."""


class AutoSubscribe(RpcEndpoint):
  """Set whether a Simple Earn locked product position auto-renews at maturity."""

  async def __call__(
    self,
    *,
    position_id: str,
    auto_subscribe: bool,
    validate: bool | None = None,
  ) -> LockedAutoSubscribeResult:
    """Set whether a Simple Earn locked product position auto-renews at maturity.

    Args:
      position_id: Locked position identifier to change the auto-subscribe setting for.
      auto_subscribe: Whether this position should auto-renew at maturity.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#set-locked-auto-subscribe)
    """
    params: dict = {
      'positionId': position_id,
      'autoSubscribe': auto_subscribe,
    }
    _Response = LockedAutoSubscribeResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/simple-earn/locked/setAutoSubscribe',
      params=params,
      validator=_validator,
      validate=validate,
    )
