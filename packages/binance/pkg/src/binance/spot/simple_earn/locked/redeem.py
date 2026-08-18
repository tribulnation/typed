from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LockedRedemption(TypedDict):
  """Result of a locked product redemption."""

  redeemId: NotRequired[int]
  """Identifier of the created redemption."""
  success: NotRequired[bool]
  """Whether the redemption succeeded."""


class Redeem(RpcEndpoint):
  """Redeem a Simple Earn locked product position."""

  async def __call__(
    self,
    *,
    position_id: str,
    validate: bool | None = None,
  ) -> LockedRedemption:
    """Redeem a Simple Earn locked product position.

    Args:
      position_id: Locked position identifier to redeem.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#redeem-locked-product)
    """
    params: dict = {
      'positionId': position_id,
    }
    _Response = LockedRedemption
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/simple-earn/locked/redeem',
      params=params,
      validator=_validator,
      validate=validate,
    )
