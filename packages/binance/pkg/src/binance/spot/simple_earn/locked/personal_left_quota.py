from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LockedPersonalLeftQuota(TypedDict):
  """This account's remaining personal subscription quota for a locked product."""

  leftPersonalQuota: NotRequired[str]
  """Remaining amount this account may still subscribe, as a decimal string."""


class PersonalLeftQuota(RpcEndpoint):
  """Get this account's remaining personal subscription quota for a Simple Earn locked product."""

  async def __call__(
    self,
    *,
    project_id: str,
    validate: bool | None = None,
  ) -> LockedPersonalLeftQuota:
    """Get this account's remaining personal subscription quota for a Simple Earn locked product.

    Args:
      project_id: Locked product identifier to check remaining personal subscription quota for.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-locked-personal-left-quota)
    """
    params: dict = {
      'projectId': project_id,
    }
    _Response = LockedPersonalLeftQuota
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/simple-earn/locked/personalLeftQuota',
      params=params,
      validator=_validator,
      validate=validate,
    )
