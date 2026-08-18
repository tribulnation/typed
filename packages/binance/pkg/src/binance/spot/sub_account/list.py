from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SubAccountListItem(TypedDict):
  """One sub-account under the master account."""

  subUserId: NotRequired[int]
  """Sub-account user id."""
  email: NotRequired[str]
  """Sub-account email."""
  remark: NotRequired[str]
  """Free-text remark set on the sub-account."""
  isFreeze: NotRequired[bool]
  """Whether the sub-account is frozen."""
  createTime: NotRequired[int]
  """Time the sub-account was created."""
  isManagedSubAccount: NotRequired[bool]
  """Whether this is a Managed Sub-Account."""
  isAssetManagementSubAccount: NotRequired[bool]
  """Whether this is an Asset Management (custody) sub-account."""


class SubAccountList(TypedDict):
  """The matching sub-accounts."""

  subAccounts: NotRequired[list[SubAccountListItem]]
  """Sub-accounts on this page."""


class List(RpcEndpoint):
  """Query the master account's sub-account list."""

  async def __call__(
    self,
    *,
    email: str | None = None,
    is_freeze: str | None = None,
    page: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> SubAccountList:
    """Query the master account's sub-account list.

    Args:
      email: Filter to one sub-account's email.
      is_freeze: Filter by freeze status: `"true"` or `"false"`.
      page: Page number.
      limit: Page size.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/account-management#query-sub-account-list)
    """
    params = {}
    if email is not None:
      params['email'] = email
    if is_freeze is not None:
      params['isFreeze'] = is_freeze
    if page is not None:
      params['page'] = page
    if limit is not None:
      params['limit'] = limit
    _Response = SubAccountList
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/list',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def paged(
    self,
    *,
    email: str | None = None,
    is_freeze: str | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[SubAccountList]:
    """Yield successive pages of this endpoint.

    Requests `page` from 1 upwards and stops on the first page shorter than `limit`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.__call__(
        email=email, is_freeze=is_freeze, limit=limit, page=page, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('subAccounts') if response is not None else None
      if not rows or (limit is not None and len(rows) < limit):
        break
      page += 1
