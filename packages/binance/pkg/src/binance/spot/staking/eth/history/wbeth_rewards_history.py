from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class WbethReward(TypedDict):
  """One WBETH reward accrual event."""

  time: NotRequired[int]
  """Millisecond epoch time of this reward accrual."""
  amountInETH: NotRequired[str]
  """Reward amount for this event, denominated in ETH, as a decimal string."""
  holding: NotRequired[str]
  """WBETH holding balance after this event, as a decimal string."""
  holdingInETH: NotRequired[str]
  """WBETH holding balance after this event, denominated in ETH, as a decimal string."""
  annualPercentageRate: NotRequired[str]
  """Annual percentage rate in effect for this event, as a decimal string."""


class WbethRewardsHistoryPage(TypedDict):
  """This account's estimated WBETH rewards and one page of reward events."""

  estRewardsInETH: NotRequired[str]
  """Estimated cumulative rewards across the queried window, denominated in ETH, as a decimal string."""
  rows: NotRequired[list[WbethReward]]
  """Matching reward events on this page."""
  total: NotRequired[int]
  """Total number of matching records across all pages."""


class WbethRewardsHistory(RpcEndpoint):
  """Query this account's WBETH staking rewards history."""

  async def wbeth_rewards_history(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> WbethRewardsHistoryPage:
    """Query this account's WBETH staking rewards history.

    Args:
      start_time: Millisecond epoch start of the queried window. See the endpoint notes for the default window applied when this and `endTime` are omitted.
      end_time: Millisecond epoch end of the queried window. See the endpoint notes for the default window applied when this and `startTime` are omitted.
      current: Page index, starting from 1.
      size: Number of records to return per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/eth-staking#get-wbeth-rewards-history)
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
    _Response = WbethRewardsHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/eth-staking/eth/history/wbethRewardsHistory',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def wbeth_rewards_history_paged(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[WbethRewardsHistoryPage]:
    """Yield successive pages of `wbeth_rewards_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.wbeth_rewards_history(
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
