"""`GET /api/v2/sub/user` — account.sub_account.list_summary."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class SubAccountSummary(TypedDict):
  userId: str
  """Sub-account's internal user id."""
  uid: int
  """Sub-account's numeric UID."""
  subName: str
  """Sub-account name."""
  status: Literal[2, 3]
  """Sub-account status."""
  type: Literal[0, 1, 2, 5]
  """Sub-account type: 0 normal, 1 robot, 2 novice (new financial), 5 hosted (asset management)."""
  access: str
  """Sub-account's granted trading permission(s)."""
  createdAt: Timestamp
  """Time the sub-account was created."""
  remarks: str
  """Remarks set at creation."""
  tradeTypes: list[str]
  """Trading permission(s) granted to the sub-account (e.g. `Spot`, `Futures`, `Margin`)."""
  openedTradeTypes: list[str]
  """Trading permission(s) actually activated by logging into the sub-account -- a granted permission (`tradeTypes`) is not active until the sub-account owner opens the corresponding product page."""
  hostedStatus: str | None
  """Asset-management hosting status; `null` for a normal sub-account."""


class SubAccountSummaryPage(TypedDict):
  currentPage: int
  """Page number returned."""
  pageSize: int
  """Results per page."""
  totalNum: int
  """Total number of sub-accounts."""
  totalPage: int
  """Total number of pages."""
  items: list[SubAccountSummary]
  """Sub-accounts on this page."""


_Type = SubAccountSummaryPage
adapter = validator[_Type](_Type)  # type: ignore


class ListSummary(RpcEndpoint):
  """`account.sub_account.list_summary` — mixed into `SubAccount`, the product exposing `account.sub_account.list_summary`."""

  async def list_summary(
    self,
    *,
    current_page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> SubAccountSummaryPage:
    """Get a paginated summary list of the master account's sub-accounts: name, status, type and granted/activated trading permissions for each.

    Args:
      current_page: Page number to fetch, starting at 1.
      page_size: Results per page.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if current_page is not None:
      params['currentPage'] = current_page
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v2/sub/user',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def list_summary_paged(
    self,
    *,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[SubAccountSummaryPage]:
    """Yield successive pages of `list_summary`.

    Requests `currentPage` from 1 upwards and stops once it has covered the `totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    current_page = 1
    pages = 0
    while True:
      response = await self.list_summary(
        page_size=page_size, current_page=current_page, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('totalPage') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or pages >= total:
        break
      current_page += 1
