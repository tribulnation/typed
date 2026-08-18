from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class RwusdSubscriptionHistoryEntry(TypedDict):
  """One RWUSD subscription."""

  time: NotRequired[int]
  """Millisecond epoch time the subscription was recorded."""
  asset: NotRequired[Literal['USDC', 'USDT']]
  """Asset subscribed with."""
  amount: NotRequired[str]
  """Subscribed amount, as a decimal string."""
  receiveAsset: NotRequired[str]
  """Asset credited to the account (always RWUSD)."""
  receiveAmount: NotRequired[str]
  """Amount credited to the account, as a decimal string."""
  status: NotRequired[str]
  """Subscription status."""


class RwusdSubscriptionHistoryPage(TypedDict):
  """One page of this account's RWUSD subscription history."""

  rows: NotRequired[list[RwusdSubscriptionHistoryEntry]]
  """Matching records on this page."""
  total: NotRequired[int]
  """Total number of matching records."""


class SubscriptionHistory(RpcEndpoint):
  """Get this account's RWUSD subscription history, sorted descending by time."""

  async def subscription_history(
    self,
    *,
    asset: Literal['USDC', 'USDT'] | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> RwusdSubscriptionHistoryPage:
    """Get this account's RWUSD subscription history, sorted descending by time.

    Args:
      asset: Restrict results to this asset.
      start_time: Millisecond epoch start of the queried window.
      end_time: Millisecond epoch end of the queried window.
      current: Currently querying page. Starts from 1.
      size: Number of results per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#get-rwusd-subscription-history)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = RwusdSubscriptionHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/rwusd/history/subscriptionHistory',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def subscription_history_paged(
    self,
    *,
    asset: Literal['USDC', 'USDT'] | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[RwusdSubscriptionHistoryPage]:
    """Yield successive pages of `subscription_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.subscription_history(
        asset=asset,
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
