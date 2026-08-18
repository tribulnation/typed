from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BnsolBoostReward(TypedDict):
  """One Boost APR reward component."""

  boostAPR: NotRequired[str]
  """Boost annual percentage rate contributed by this reward component, as a decimal string."""
  rewardsAsset: NotRequired[str]
  """Asset this Boost APR component pays rewards in."""


class BnsolRate(TypedDict):
  """BNSOL/SOL exchange rate and APR at a point in time."""

  annualPercentageRate: NotRequired[str]
  """Base annual percentage rate in effect at this time, as a decimal string."""
  exchangeRate: NotRequired[str]
  """BNSOL/SOL exchange rate at this time, as a decimal string."""
  boostRewards: NotRequired[list[BnsolBoostReward]]
  """Boost APR reward components in effect at this time, if any."""
  time: NotRequired[int]
  """Millisecond epoch time this rate was in effect."""


class BnsolRateHistoryPage(TypedDict):
  """One page of BNSOL rate history."""

  rows: NotRequired[list[BnsolRate]]
  """Matching rate records on this page."""
  total: NotRequired[int]
  """Total number of matching records across all pages."""


class RateHistory(RpcEndpoint):
  """Query historical BNSOL/SOL exchange rates and APR, including any Boost APR components."""

  async def rate_history(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> BnsolRateHistoryPage:
    """Query historical BNSOL/SOL exchange rates and APR, including any Boost APR components.

    Args:
      start_time: Millisecond epoch start of the queried window. See the endpoint notes for the default window applied when this and `endTime` are omitted.
      end_time: Millisecond epoch end of the queried window. See the endpoint notes for the default window applied when this and `startTime` are omitted.
      current: Page index, starting from 1.
      size: Number of records to return per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/sol-staking#get-bnsol-rate-history)
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
    _Response = BnsolRateHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sol-staking/sol/history/rateHistory',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def rate_history_paged(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[BnsolRateHistoryPage]:
    """Yield successive pages of `rate_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.rate_history(
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
