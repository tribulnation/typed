"""`GET /api/v1/broker/nd/account` — Get sub-account."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class BrokerSubAccount(TypedDict):
  """One broker sub-account."""

  accountName: str
  uid: str
  createdAt: Timestamp
  level: int
  """Sub-account VIP level."""


class SubAccountsResult(TypedDict):
  """One page of a broker's sub-accounts."""

  currentPage: int
  pageSize: int
  totalNum: int
  totalPage: int
  items: list[BrokerSubAccount]


adapter = validator(SubAccountsResult)


class SubAccounts(RpcEndpoint):
  """`Get sub-account` — mixed into `Broker`, the product exposing
  `broker.sub_accounts`."""

  async def sub_accounts(
    self,
    *,
    uid: str | None = None,
    current_page: int = 1,
    page_size: int = 20,
    validate: bool | None = None,
  ) -> SubAccountsResult:
    """List the broker's sub-accounts.

    Args:
      uid: Restrict the response to one sub-account UID. Omit for every sub-account.
      current_page: Page to fetch, starting at 1.
      page_size: Rows per page, up to 100.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {'currentPage': current_page, 'pageSize': page_size}
    if uid is not None:
      params['uid'] = uid
    return await self.authed_request(
      'GET',
      '/api/v1/broker/nd/account',
      params=params,
      validator=adapter,
      validate=validate,
    )
