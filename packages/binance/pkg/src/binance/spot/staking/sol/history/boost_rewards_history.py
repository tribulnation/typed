from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BoostReward(TypedDict):
  """One Boost APR reward event."""

  time: NotRequired[int]
  """Millisecond epoch time of this event."""
  token: NotRequired[str]
  """Asset this reward event is denominated in."""
  amount: NotRequired[str]
  """Amount for this event, as a decimal string."""
  bnsolHolding: NotRequired[str]
  """BNSOL holding balance at the time of this event, as a decimal string."""
  status: NotRequired[str]
  """Event status."""


class BoostRewardsHistoryPage(TypedDict):
  """One page of Boost APR reward history."""

  rows: NotRequired[list[BoostReward]]
  """Matching boostreward records on this page."""
  total: NotRequired[int]
  """Total number of matching records across all pages."""


class BoostRewardsHistory(RpcEndpoint):
  """Query this account's Boost APR airdrop reward history, filtered by event type."""

  async def boost_rewards_history(
    self,
    *,
    type: Literal['CLAIM', 'DISTRIBUTE'],
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> BoostRewardsHistoryPage:
    """Query this account's Boost APR airdrop reward history, filtered by event type.

    Args:
      type: Event type to filter by.
      start_time: Millisecond epoch start of the queried window. See the endpoint notes for the default window applied when this and `endTime` are omitted.
      end_time: Millisecond epoch end of the queried window. See the endpoint notes for the default window applied when this and `startTime` are omitted.
      current: Page index, starting from 1.
      size: Number of records to return per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/sol-staking#get-boost-rewards-history)
    """
    params: dict = {
      'type': type,
    }
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = BoostRewardsHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sol-staking/sol/history/boostRewardsHistory',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def boost_rewards_history_paged(
    self,
    *,
    type: Literal['CLAIM', 'DISTRIBUTE'],
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[BoostRewardsHistoryPage]:
    """Yield successive pages of `boost_rewards_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.boost_rewards_history(
        type=type,
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
