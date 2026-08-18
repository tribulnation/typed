"""`GET /api/v2/broker/queryMyCommission` — Get Commission."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BrokerCommission(TypedDict):
  """One broker commission record for a settlement period."""

  siteType: str
  """Site the commission originated from, e.g. `europe`."""
  rebateType: Literal[0, 1, 2]
  """Rebate type. KuCoin's docs list the allowed values without stating what each one means."""
  payoutTime: int
  """Commission payout time, Unix milliseconds."""
  periodStartTime: int
  """Start of the commission calculation period, Unix milliseconds."""
  periodEndTime: int
  """End of the commission calculation period, Unix milliseconds."""
  status: int
  """Payout status. KuCoin's docs give no closed set or meaning for this field; left bare rather than an invented enum."""
  totalTradeUser: str
  """Number of users who traded in this period."""
  tagUser: str
  """Number of tagged users who traded in this period."""
  tagTradeVolume: str
  """Trading volume contributed by tagged users."""
  tagCommission: str
  """Commission contributed by tagged users."""
  invitedUser: str
  """Number of invited users active in this period."""
  noTagTradeVolume: str
  """Trading volume contributed by untagged users."""
  noTagCommission: str
  """Commission contributed by untagged users."""
  totalCommission: str
  """Total commission for this period."""
  currency: str
  """Denomination unit for the volume/amount fields, e.g. `USDT`."""


class BrokerCommissionResult(TypedDict):
  """One page of a broker's commission records."""

  currentPage: int
  """Current page number."""
  pageSize: int
  """Number of items per page."""
  totalNum: int
  """Total number of items."""
  totalPage: int
  """Total number of pages."""
  items: list[BrokerCommission]
  """Commission records on this page."""


_Type = BrokerCommissionResult
adapter = validator[_Type](_Type)  # type: ignore


class Commission(RpcEndpoint):
  """`Get Commission` — mixed into `Broker`, the product exposing `broker.commission`."""

  async def commission(
    self,
    *,
    site_type: str | None = None,
    trade_type: Literal['all', 'SPOT', 'FUTURE'] | None = None,
    rebate_type: Literal['1', '2'] | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> BrokerCommissionResult:
    """Page through the authenticated API Broker's own commission records: per-period payout, trading volume and rebate, broken out by whether the underlying trades carried a broker tag. Distinct from the Affiliate program's own `affiliate.commission` (different product, different response shape) and from the Exchange (ND) Broker rebate-download endpoints (`broker.rebate_download`/`broker.rebate_download_v3`), which return a CSV link rather than paged JSON rows.

    Args:
      site_type: The site from which the commission originates. KuCoin's docs document no closed set for this field, only its default.
      trade_type: Trade type to restrict the commission query to.
      rebate_type: Rebate type filter. KuCoin's docs list the allowed values without stating what each one means, and the field's own example value (`0`) falls outside the declared allowed set -- see notes.
      start_at: Commission calculation start time, Unix milliseconds. If `endAt` is also given, must be earlier than it.
      end_at: Commission calculation end time, Unix milliseconds. If `startAt` is also given, must be later than it.
      page: Page number.
      page_size: Page size.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if site_type is not None:
      params['siteType'] = site_type
    if trade_type is not None:
      params['tradeType'] = trade_type
    if rebate_type is not None:
      params['rebateType'] = rebate_type
    if start_at is not None:
      params['startAt'] = start_at
    if end_at is not None:
      params['endAt'] = end_at
    if page is not None:
      params['page'] = page
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v2/broker/queryMyCommission',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def commission_paged(
    self,
    *,
    site_type: str | None = None,
    trade_type: Literal['all', 'SPOT', 'FUTURE'] | None = None,
    rebate_type: Literal['1', '2'] | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[BrokerCommissionResult]:
    """Yield successive pages of `commission`.

    Requests `page` from 1 upwards and stops once it has covered the `totalPage` pages
    the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.commission(
        site_type=site_type,
        trade_type=trade_type,
        rebate_type=rebate_type,
        start_at=start_at,
        end_at=end_at,
        page_size=page_size,
        page=page,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('totalPage') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or pages >= total:
        break
      page += 1
