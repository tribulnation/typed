from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class RebateRecord(TypedDict):
  """One rebate or referral-kickback record."""

  asset: NotRequired[str]
  """Rebate asset."""
  type: NotRequired[int]
  """Rebate type: 1 commission rebate, 2 referral kickback."""
  amount: NotRequired[str]
  """Rebate amount."""
  updateTime: NotRequired[int]
  """Millisecond epoch update timestamp."""


class RebateTaxQueryData(TypedDict):
  """Paged rebate records."""

  page: NotRequired[int]
  """Current page number."""
  totalRecords: NotRequired[int]
  """Total number of matching records."""
  totalPageNum: NotRequired[int]
  """Total number of pages."""
  data: NotRequired[list[RebateRecord]]
  """Rebate records for this page."""


class RebateTaxQueryResponse(TypedDict):
  """Rebate history response frame. This product line wraps its business data in {status,type,code,data} on the wire, and the core does not strip it -- see spec/core.md's Envelope section."""

  status: NotRequired[str]
  """Response status, e.g. "OK"."""
  type: NotRequired[str]
  """Response type, e.g. "GENERAL"."""
  code: NotRequired[str]
  """Response code."""
  data: NotRequired[RebateTaxQueryData]


class TaxQuery(RpcEndpoint):
  """Query this account's spot commission-rebate and referral-kickback history."""

  async def tax_query(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> RebateTaxQueryResponse:
    """Query this account's spot commission-rebate and referral-kickback history.

    Args:
      start_time: Millisecond epoch start of the queried window. If omitted along with `endTime`, the recent 7 days are returned.
      end_time: Millisecond epoch end of the queried window. Max interval from `startTime` is 30 days.
      page: Page number.

    References:
      - [Official docs](https://developers.binance.com/docs/rebate/rest-api/Get-Spot-Rebate-History-Records)
    """
    params = {}
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if page is not None:
      params['page'] = page
    _Response = RebateTaxQueryResponse
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/rebate/taxQuery',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def tax_query_paged(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[RebateTaxQueryResponse]:
    """Yield successive pages of `tax_query`.

    Requests `page` from 1 upwards and stops once it has covered the `data.totalPageNum`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.tax_query(
        start_time=start_time, end_time=end_time, page=page, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total_0 = response.get('data') if response is not None else None
      total = total_0.get('totalPageNum') if total_0 is not None else None
      total = int(total) if total is not None else None
      if total is None or pages >= total:
        break
      page += 1
