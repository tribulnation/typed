"""`POST /api/v3/sub/user/futures/enable` — account.sub_account.add_futures_permission."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class AddSubAccountFuturesPermissionRequest(TypedDict):
  uid: str
  """Sub-account UID to grant Futures permission to."""


_Type = bool | None
adapter = validator[_Type](_Type)  # type: ignore


class AddFuturesPermission(RpcEndpoint):
  """`account.sub_account.add_futures_permission` — mixed into `SubAccount`, the product exposing `account.sub_account.add_futures_permission`."""

  async def add_futures_permission(
    self,
    add_sub_account_futures_permission_request: AddSubAccountFuturesPermissionRequest,
    *,
    validate: bool | None = None,
  ) -> bool | None:
    """Grant Futures trading permission to an existing sub-account. The master account's API key must itself carry Futures permission and have Futures trading activated before this call succeeds.

    Args:
      add_sub_account_futures_permission_request: Sub-account to grant Futures permission to.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/sub/user/futures/enable',
      json=add_sub_account_futures_permission_request,
      validator=adapter,
      validate=validate,
    )
