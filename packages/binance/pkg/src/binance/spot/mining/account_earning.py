from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MiningAccountEarningRecord(TypedDict):
  """One sub-account earnings record."""

  time: NotRequired[int]
  """Millisecond epoch record timestamp."""
  coinName: NotRequired[str]
  """Coin the earnings are denominated in."""
  type: NotRequired[int]
  """Earnings type."""
  puid: NotRequired[int]
  """Sub-account's Binance UID."""
  subName: NotRequired[str]
  """Sub-account mining name."""
  amount: NotRequired[float]
  """Earnings amount."""


class MiningAccountEarningData(TypedDict):
  """Paged sub-account earnings."""

  accountProfits: NotRequired[list[MiningAccountEarningRecord]]
  """Sub-account earnings on this page."""
  totalNum: NotRequired[int]
  """Total number of matching records."""
  pageSize: NotRequired[int]
  """Number of records returned per page."""


class MiningAccountEarningResponse(TypedDict):
  """Mining account earning response frame. This product line wraps its business data in {code,msg,data} on the wire, and the core does not strip it -- see spec/core.md's Envelope section."""

  code: NotRequired[int]
  """Response code. 0 indicates success."""
  msg: NotRequired[str]
  """Response message."""
  data: NotRequired[MiningAccountEarningData]


class AccountEarning(RpcEndpoint):
  """Query earnings across this mining account's sub-accounts."""

  async def account_earning(
    self,
    *,
    algo: str,
    start_date: int | None = None,
    end_date: int | None = None,
    page_index: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> MiningAccountEarningResponse:
    """Query earnings across this mining account's sub-accounts.

    Args:
      algo: Mining algorithm, e.g. sha256.
      start_date: Millisecond epoch start of the queried window.
      end_date: Millisecond epoch end of the queried window.
      page_index: Page number.
      page_size: Number of rows per page.

    References:
      - [Official docs](https://developers.binance.com/docs/mining/rest-api#mining-account-earning)
    """
    params: dict = {
      'algo': algo,
    }
    if start_date is not None:
      params['startDate'] = start_date
    if end_date is not None:
      params['endDate'] = end_date
    if page_index is not None:
      params['pageIndex'] = page_index
    if page_size is not None:
      params['pageSize'] = page_size
    _Response = MiningAccountEarningResponse
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/mining/payment/uid',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def account_earning_paged(
    self,
    *,
    algo: str,
    start_date: int | None = None,
    end_date: int | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[MiningAccountEarningResponse]:
    """Yield successive pages of `account_earning`.

    Requests `pageIndex` from 1 upwards and stops once it has covered the
    `data.totalNum` items the response reports, or after `max_pages` pages when one is
    given.
    """
    page_index = 1
    pages = 0
    while True:
      response = await self.account_earning(
        algo=algo,
        start_date=start_date,
        end_date=end_date,
        page_size=page_size,
        page_index=page_index,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total_0 = response.get('data') if response is not None else None
      total = total_0.get('totalNum') if total_0 is not None else None
      total = int(total) if total is not None else None
      if total is None or page_size is None or pages * page_size >= total:
        break
      page_index += 1
