from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class RwusdRewardsHistoryEntry(TypedDict):
  """One RWUSD reward."""

  time: NotRequired[int]
  """Millisecond epoch time the reward was recorded."""
  rewardsAmount: NotRequired[str]
  """Reward amount, as a decimal string."""
  rwusdPosition: NotRequired[str]
  """RWUSD position size at the time of the reward, as a decimal string."""
  annualPercentageRate: NotRequired[str]
  """Annual percentage rate in effect at `time`, as a decimal string."""


class RwusdRewardsHistoryPage(TypedDict):
  """One page of this account's RWUSD rewards history."""

  rows: NotRequired[list[RwusdRewardsHistoryEntry]]
  """Matching records on this page."""
  total: NotRequired[int]
  """Total number of matching records."""


class RewardsHistory(RpcEndpoint):
  """Get this account's RWUSD rewards history, sorted descending by time."""

  async def rewards_history(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> RwusdRewardsHistoryPage:
    """Get this account's RWUSD rewards history, sorted descending by time.

    Args:
      start_time: Millisecond epoch start of the queried window.
      end_time: Millisecond epoch end of the queried window.
      current: Currently querying page. Starts from 1.
      size: Number of results per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#get-rwusd-rewards-history)
    """
    params = {}
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = RwusdRewardsHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/rwusd/history/rewardsHistory',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def rewards_history_paged(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[RwusdRewardsHistoryPage]:
    """Yield successive pages of `rewards_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.rewards_history(
        start_time=start_time,
        end_time=end_time,
        size=size,
        current=current,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or size is None or pages * size >= total:
        break
      current += 1
