from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.futures.core import AuthFuturesMixin

class FundingRecordsItem(TypedDict):
  """funding record"""
  id: int | str
  """Funding record id."""
  symbol: str
  """Contract symbol."""
  positionId: NotRequired[int | str]
  """Position id when present."""
  positionType: Literal[1, 2]
  """Position side: 1 long, 2 short."""
  positionValue: float
  """Position value used for funding."""
  funding: float
  """Funding amount."""
  rate: float
  """Funding rate."""
  settleTime: Timestamp | Timestamp
  """Funding settlement time."""

class FundingRecordsData(TypedDict):
  """Funding record page."""
  pageSize: int
  """Number of records requested per page."""
  totalCount: int
  """Total number of matching records."""
  totalPage: int
  """Total number of available pages."""
  currentPage: int
  """Current page number."""
  resultList: list[FundingRecordsItem]
  """Page of funding record records."""

class FundingRecordsResponse(TypedDict):
  """Get user funding records response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[FundingRecordsData]

adapter = validator(FundingRecordsResponse)

class FundingRecords(AuthFuturesMixin):
  async def funding_records(
    self, *,
    symbol: str | None = None, position_id: int | None = None, page_num: int,
    page_size: int, validate: bool | None = None,
  ) -> FundingRecordsResponse:
    """Returns paginated funding-fee records for the signed futures account.

    Args:
      symbol: Optional contract symbol filter.
      position_id: Optional position id filter.
      page_num: Page number; default is 1.
      page_size: Page size; default 20, maximum 100.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-details-of-user-s-funding-rate)
    """
    headers = {}
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if position_id is not None:
      params['position_id'] = position_id
    if page_num is not None:
      params['page_num'] = page_num
    if page_size is not None:
      params['page_size'] = page_size
    r = await self.signed_request('GET', '/api/v1/private/position/funding_records', params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)

  async def funding_records_paged(
    self, *,
    symbol: str | None = None, position_id: int | None = None, page_size: int,
    max_pages: int | None = None, validate: bool | None = None,
  ) -> AsyncIterator[FundingRecordsResponse]:
    """Yield successive pages of `funding_records`.

    Requests `page_num` from 1 upwards and stops once it has covered the
    `data.totalPage` pages the response reports, or after `max_pages` pages when one is
    given.
    """
    page_num = 1
    pages = 0
    while True:
      response = await self.funding_records(symbol=symbol, position_id=position_id, page_size=page_size, page_num=page_num, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total_0 = response.get('data') if response is not None else None
      total = total_0.get('totalPage') if total_0 is not None else None
      total = int(total) if total is not None else None
      if total is None or pages >= total:
        break
      page_num += 1
