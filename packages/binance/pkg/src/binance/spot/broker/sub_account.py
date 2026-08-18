from typing_extensions import AsyncIterator, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BrokerSubAccount(TypedDict):
  """One sub-account."""

  subaccountId: str
  """Sub-account identifier."""
  email: str
  """Sub-account email."""
  tag: str
  """Tag supplied at creation, if any."""
  makerCommission: float
  """Spot maker commission rate for this sub-account."""
  takerCommission: float
  """Spot taker commission rate for this sub-account."""
  marginMakerCommission: float
  """Margin maker commission rate override, or `-1` if unset."""
  marginTakerCommission: float
  """Margin taker commission rate override, or `-1` if unset."""
  createTime: Timestamp
  """Time this sub-account was created."""


class SubAccount(RpcEndpoint):
  """Query Sub Account"""

  async def sub_account(
    self,
    *,
    sub_account_id: str | None = None,
    page: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> list[BrokerSubAccount]:
    """List sub-accounts under this broker account.

    Args:
      sub_account_id: Sub-account identifier. All sub-accounts if omitted.
      page: Page number, 1-indexed. Default 1.
      size: Records per page. Default 500, max 500.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params = {}
    if sub_account_id is not None:
      params['subAccountId'] = sub_account_id
    if page is not None:
      params['page'] = page
    if size is not None:
      params['size'] = size
    _Response = list[BrokerSubAccount]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/broker/subAccount',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def sub_account_paged(
    self,
    *,
    sub_account_id: str | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[BrokerSubAccount]]:
    """Yield successive pages of `sub_account`.

    Requests `page` from 1 upwards and stops on the first page shorter than `size`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.sub_account(
        sub_account_id=sub_account_id, size=size, page=page, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      if not response or (size is not None and len(response) < size):
        break
      page += 1
