"""`POST /api/v3/sub/user/margin/enable` — account.sub_account.add_margin_permission."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class AddSubAccountMarginPermissionRequest(TypedDict):
  uid: str
  """Sub-account UID to grant Margin permission to."""


_Type = str | None
adapter = validator[_Type](_Type)  # type: ignore


class AddMarginPermission(RpcEndpoint):
  """`account.sub_account.add_margin_permission` — mixed into `SubAccount`, the product exposing `account.sub_account.add_margin_permission`."""

  async def add_margin_permission(
    self,
    add_sub_account_margin_permission_request: AddSubAccountMarginPermissionRequest,
    *,
    validate: bool | None = None,
  ) -> str | None:
    """Grant Margin trading permission to an existing sub-account. The master account's API key must itself carry Margin permission and have Margin trading activated before this call succeeds.

    Args:
      add_sub_account_margin_permission_request: Sub-account to grant Margin permission to.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/sub/user/margin/enable',
      json=add_sub_account_margin_permission_request,
      validator=adapter,
      validate=validate,
    )
