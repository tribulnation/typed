from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class WbethWrap(TypedDict):
  """One BETH-to-WBETH wrap event."""

  time: NotRequired[int]
  """Millisecond epoch time the wrap was requested."""
  fromAsset: NotRequired[str]
  """Asset wrapped from (BETH)."""
  fromAmount: NotRequired[str]
  """Amount of `fromAsset` wrapped, as a decimal string."""
  toAsset: NotRequired[str]
  """Asset wrapped into (WBETH)."""
  toAmount: NotRequired[str]
  """Amount of `toAsset` received, as a decimal string."""
  exchangeRate: NotRequired[str]
  """Exchange rate applied to this wrap, as a decimal string."""
  status: NotRequired[str]
  """Wrap status."""


class WbethWrapHistoryPage(TypedDict):
  """One page of WBETH wrap history."""

  rows: NotRequired[list[WbethWrap]]
  """Matching wbethwrap records on this page."""
  total: NotRequired[int]
  """Total number of matching records across all pages."""


class WrapHistory(RpcEndpoint):
  """Query this account's BETH-to-WBETH wrap history."""

  async def wrap_history(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> WbethWrapHistoryPage:
    """Query this account's BETH-to-WBETH wrap history.

    Args:
      start_time: Millisecond epoch start of the queried window. See the endpoint notes for the default window applied when this and `endTime` are omitted.
      end_time: Millisecond epoch end of the queried window. See the endpoint notes for the default window applied when this and `startTime` are omitted.
      current: Page index, starting from 1.
      size: Number of records to return per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/eth-staking#get-wbeth-wrap-history)
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
    _Response = WbethWrapHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/eth-staking/wbeth/history/wrapHistory',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def wrap_history_paged(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[WbethWrapHistoryPage]:
    """Yield successive pages of `wrap_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.wrap_history(
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
