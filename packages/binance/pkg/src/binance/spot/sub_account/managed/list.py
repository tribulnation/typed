from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class ManagedSubAccountInfo(TypedDict):
  """One Managed Sub-Account."""

  rootUserId: NotRequired[int]
  """Root user id of the Managed Sub-Account."""
  managersubUserId: NotRequired[int]
  """Managed Sub-Account's own user id."""
  bindParentUserId: NotRequired[int]
  """User id of the bound trading-team parent account."""
  email: NotRequired[str]
  """Managed Sub-Account email."""
  insertTimeStamp: NotRequired[int]
  """Time the Managed Sub-Account was created."""
  bindParentEmail: NotRequired[str]
  """Email of the bound trading-team parent account."""
  isSubUserEnabled: NotRequired[bool]
  """Whether the Managed Sub-Account is enabled."""
  isUserActive: NotRequired[bool]
  """Whether the Managed Sub-Account is active."""
  isMarginEnabled: NotRequired[bool]
  """Whether Margin trading is enabled."""
  isFutureEnabled: NotRequired[bool]
  """Whether Futures trading is enabled."""
  isSignedLVTRiskAgreement: NotRequired[bool]
  """Whether the leveraged-token risk agreement has been signed."""


class ManagedSubAccountList(TypedDict):
  """The matching Managed Sub-Accounts."""

  total: NotRequired[int]
  """Total number of Managed Sub-Accounts matching the query."""
  managerSubUserInfoVoList: NotRequired[list[ManagedSubAccountInfo]]
  """Managed Sub-Accounts on this page."""


class List(RpcEndpoint):
  """Get the investor's Managed Sub-Account list."""

  async def list(
    self,
    *,
    email: str | None = None,
    page: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> ManagedSubAccountList:
    """Get the investor's Managed Sub-Account list.

    Args:
      email: Filter to one Managed Sub-Account's email.
      page: Page number.
      limit: Page size.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#query-managed-sub-account-list)
    """
    params = {}
    if email is not None:
      params['email'] = email
    if page is not None:
      params['page'] = page
    if limit is not None:
      params['limit'] = limit
    _Response = ManagedSubAccountList
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/managed-subaccount/info',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def list_paged(
    self,
    *,
    email: str | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[ManagedSubAccountList]:
    """Yield successive pages of `list`.

    Requests `page` from 1 upwards and stops once it has covered the `total` items the
    response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.list(email=email, limit=limit, page=page, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or limit is None or pages * limit >= total:
        break
      page += 1
