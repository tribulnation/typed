from typing_extensions import AsyncIterator, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BrokerSpotRebateRecord(TypedDict):
  """One spot commission rebate."""

  subaccountId: str
  """Sub-account this rebate accrued from."""
  income: str
  """Rebate amount."""
  asset: str
  """Asset the rebate was paid in."""
  symbol: str
  """Trading symbol the underlying trade was on."""
  tradeId: int
  """Trade identifier the rebate accrued from."""
  time: Timestamp
  """Time the rebate was recorded."""
  status: int
  """Rebate status. Documented example is `1`; the venue does not declare this as a closed enum."""


class CommissionRebateRecentRecordSpot(RpcEndpoint):
  """Query Broker Commission Rebate Recent Record (Spot)"""

  async def commission_rebate_recent_record_spot(
    self,
    *,
    sub_account_id: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    page: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> list[BrokerSpotRebateRecord]:
    """Get recent spot commission rebate records across sub-accounts.

    Args:
      sub_account_id: Sub-account identifier. All sub-accounts if omitted.
      start_time: Start of the query window, UTC ms. Defaults to 7 days before now.
      end_time: End of the query window, UTC ms. Defaults to now.
      page: Page number, 1-indexed. Default 1.
      size: Records per page. Default 500, max 500.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params = {}
    if sub_account_id is not None:
      params['subAccountId'] = sub_account_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if page is not None:
      params['page'] = page
    if size is not None:
      params['size'] = size
    _Response = list[BrokerSpotRebateRecord]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/broker/rebate/recentRecord',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def commission_rebate_recent_record_spot_paged(
    self,
    *,
    sub_account_id: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[BrokerSpotRebateRecord]]:
    """Yield successive pages of `commission_rebate_recent_record_spot`.

    Requests `page` from 1 upwards and stops on the first page shorter than `size`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.commission_rebate_recent_record_spot(
        sub_account_id=sub_account_id,
        start_time=start_time,
        end_time=end_time,
        size=size,
        page=page,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      if not response or (size is not None and len(response) < size):
        break
      page += 1
