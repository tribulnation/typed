from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class OnChainYieldsLockedRedemption(TypedDict):
  """Result of an On-chain Yields locked product redemption."""

  redeemId: NotRequired[int]
  """Identifier of the created redemption."""
  success: NotRequired[bool]
  """Whether the redemption succeeded."""


class Redeem(RpcEndpoint):
  """Redeem an On-chain Yields locked product position."""

  async def __call__(
    self,
    *,
    position_id: str,
    channel_id: str | None = None,
    validate: bool | None = None,
  ) -> OnChainYieldsLockedRedemption:
    """Redeem an On-chain Yields locked product position.

    Args:
      position_id: Locked position identifier to redeem.
      channel_id: Optional channel identifier for this redemption.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/on-chain-yields#redeem-on-chain-yields-locked-product)
    """
    params: dict = {
      'positionId': position_id,
    }
    if channel_id is not None:
      params['channelId'] = channel_id
    _Response = OnChainYieldsLockedRedemption
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/onchain-yields/locked/redeem',
      params=params,
      validator=_validator,
      validate=validate,
    )
