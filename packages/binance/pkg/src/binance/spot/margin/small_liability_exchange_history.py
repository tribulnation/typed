from typing_extensions import AsyncIterator, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginSmallLiabilityExchangeRecord(TypedDict):
  """A single small liability exchange."""

  asset: str
  """Liability asset that was exchanged."""
  amount: str
  """Amount of `asset` exchanged, as a decimal string."""
  targetAsset: str
  """Asset `asset` was exchanged into."""
  targetAmount: str
  """Amount of `targetAsset` received, as a decimal string."""
  bizType: str
  """Business type of this record. Only "EXCHANGE_SMALL_LIABILITY" is documented anywhere in this pass's sources (swagger's own example); left a bare string rather than guessing the rest of the set."""
  timestamp: int
  """Millisecond timestamp the exchange occurred."""


class MarginSmallLiabilityExchangeHistory(TypedDict):
  """Page of small liability exchange history."""

  total: int
  """Total number of matching records across all pages."""
  rows: list[MarginSmallLiabilityExchangeRecord]
  """Matching exchanges on this page."""


class SmallLiabilityExchangeHistory(RpcEndpoint):
  """Get Small Liability Exchange History"""

  async def small_liability_exchange_history(
    self,
    *,
    current: int | None = None,
    size: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    validate: bool | None = None,
  ) -> MarginSmallLiabilityExchangeHistory:
    """Query this margin account's history of small liability exchanges.

    Args:
      current: Page to fetch, 1-indexed.
      size: Number of records per page. Max 100.
      start_time: Query period start, as milliseconds since epoch.
      end_time: Query period end, as milliseconds since epoch.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#get-small-liability-exchange-history)
    """
    params = {}
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    _Response = MarginSmallLiabilityExchangeHistory
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/exchange-small-liability-history',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def small_liability_exchange_history_paged(
    self,
    *,
    size: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[MarginSmallLiabilityExchangeHistory]:
    """Yield successive pages of `small_liability_exchange_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.small_liability_exchange_history(
        size=size,
        start_time=start_time,
        end_time=end_time,
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
