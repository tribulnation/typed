from typing_extensions import AsyncIterator, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class SubAccountsItem(TypedDict):
  """Sub-account record."""
  subAccount: str | None
  """Sub-account name."""
  isFreeze: bool | str | None
  """Whether the sub-account is frozen."""
  createTime: Timestamp | None
  """Sub-account creation time in milliseconds."""
  uid: str | int | None
  """Sub-account user id."""

class SubAccountsResponse(TypedDict):
  """Sub-account list wrapper."""
  subAccounts: list[SubAccountsItem]
  """Sub-account records."""

Response: type[SubAccountsResponse | ErrorResponse] = SubAccountsResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class List(AuthSpotMixin):
  async def list(
    self, *,
    sub_account: str | None = None, is_freeze: str | None = None,
    page: int | None = None, limit: int | None = None,
    timestamp: Timestamp | None = None, recv_window: int | None = None,
    validate: bool | None = None,
  ) -> SubAccountsResponse:
    """Returns sub-account records visible to the signed master account.

    Args:
      sub_account: Optional sub-account name filter.
      is_freeze: Optional freeze-state filter, expressed as true or false.
      page: Result page number. Defaults to 1.
      limit: Maximum records to return. Defaults to 10 and may not exceed 200.
      timestamp: Signed request timestamp in milliseconds.
      recv_window: Optional signed-request validity window in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-sub-account-list-for-master-account)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if sub_account is not None:
      params['subAccount'] = sub_account
    if is_freeze is not None:
      params['isFreeze'] = is_freeze
    if page is not None:
      params['page'] = page
    if limit is not None:
      params['limit'] = limit
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    if recv_window is not None:
      params['recvWindow'] = recv_window
    r = await self.signed_request('GET', '/api/v3/sub-account/list', params=params)
    return self.output(r.text, adapter, validate)

  async def list_paged(
    self, *,
    sub_account: str | None = None, is_freeze: str | None = None,
    limit: int | None = None, timestamp: Timestamp | None = None,
    recv_window: int | None = None, max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[SubAccountsResponse]:
    """Yield successive pages of `list`.

    Requests `page` from 1 upwards and stops on the first page shorter than `limit`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.list(sub_account=sub_account, is_freeze=is_freeze, limit=limit, timestamp=timestamp, recv_window=recv_window, page=page, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('subAccounts') if response is not None else None
      if not rows or (limit is not None and len(rows) < limit):
        break
      page += 1
