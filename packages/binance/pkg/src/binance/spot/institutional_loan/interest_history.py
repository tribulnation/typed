from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class RiskUnitInterestHistoryEntry(TypedDict):
  """One interest history entry."""

  groupId: NotRequired[int]
  """Risk unit unique identifier."""
  assetName: NotRequired[str]
  """Liability asset name."""
  principal: NotRequired[float]
  """Principal on which interest was charged."""
  interestRate: NotRequired[float]
  """Interest rate applied."""
  interest: NotRequired[float]
  """Interest amount charged."""
  interestTimestamp: NotRequired[int]
  """Interest charge timestamp, in milliseconds."""


class RiskUnitInterestHistoryPage(TypedDict):
  """One page of risk unit interest history."""

  total: NotRequired[int]
  """Number of historical interest records."""
  rows: NotRequired[list[RiskUnitInterestHistoryEntry]]
  """Interest history records."""


class InterestHistory(RpcEndpoint):
  """Query institutional loan risk unit interest history. Callable only with the credit account API key. When `groupId` is omitted, only currently activated risk units are returned; when provided, both activated and closed risk units can be queried. Results are returned in descending order. The max interval between `startTime` and `endTime` is 100 days. If neither is provided, the last 7 days are returned by default. If only `startTime` is provided, records in `[max(startTime, now - 30d), now]` are returned; if only `endTime` is provided, records in `[endTime - 7d, endTime]` are returned."""

  async def interest_history(
    self,
    *,
    group_id: int | None = None,
    asset: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> RiskUnitInterestHistoryPage:
    """Query institutional loan risk unit interest history. Callable only with the credit account API key. When `groupId` is omitted, only currently activated risk units are returned; when provided, both activated and closed risk units can be queried. Results are returned in descending order. The max interval between `startTime` and `endTime` is 100 days. If neither is provided, the last 7 days are returned by default. If only `startTime` is provided, records in `[max(startTime, now - 30d), now]` are returned; if only `endTime` is provided, records in `[endTime - 7d, endTime]` are returned.

    Args:
      group_id: Risk unit unique identifier.
      asset: Asset name to filter by, for example `USDT` or `USDC`.
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      current: Current page number. Starts from 1.
      size: Number of records per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-institutional-loan/api/rest-api/borrow-repay#risk-unit-interest-history)
    """
    params = {}
    if group_id is not None:
      params['groupId'] = group_id
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
    _Response = RiskUnitInterestHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/loan-group/interest-history',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def interest_history_paged(
    self,
    *,
    group_id: int | None = None,
    asset: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[RiskUnitInterestHistoryPage]:
    """Yield successive pages of `interest_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.interest_history(
        group_id=group_id,
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
