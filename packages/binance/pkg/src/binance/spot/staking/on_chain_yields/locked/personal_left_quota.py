from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class OnChainYieldsLockedPersonalLeftQuota(TypedDict):
  """This account's remaining personal subscription quota for a locked product."""

  leftPersonalQuota: NotRequired[str]
  """Remaining amount this account may still subscribe, as a decimal string."""


class PersonalLeftQuota(RpcEndpoint):
  """Get this account's remaining personal subscription quota for an On-chain Yields locked product."""

  async def __call__(
    self,
    *,
    project_id: str,
    validate: bool | None = None,
  ) -> OnChainYieldsLockedPersonalLeftQuota:
    """Get this account's remaining personal subscription quota for an On-chain Yields locked product.

    Args:
      project_id: Locked product identifier to check remaining personal subscription quota for.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/on-chain-yields#get-on-chain-yields-locked-personal-left-quota)
    """
    params: dict = {
      'projectId': project_id,
    }
    _Response = OnChainYieldsLockedPersonalLeftQuota
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/onchain-yields/locked/personalLeftQuota',
      params=params,
      validator=_validator,
      validate=validate,
    )
