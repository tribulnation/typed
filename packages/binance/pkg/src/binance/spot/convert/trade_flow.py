from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from typed_core.exceptions import LogicError
from binance.core.endpoint.rpc import RpcEndpoint


class ConvertTrade(TypedDict):
  """One completed Convert trade."""

  quoteId: NotRequired[str]
  """Quote identifier the trade was accepted from."""
  orderId: NotRequired[int]
  """Order identifier."""
  orderStatus: NotRequired[str]
  """Final order status."""
  fromAsset: NotRequired[str]
  """Asset debited."""
  fromAmount: NotRequired[str]
  """Amount debited."""
  toAsset: NotRequired[str]
  """Asset credited."""
  toAmount: NotRequired[str]
  """Amount credited."""
  ratio: NotRequired[str]
  """Conversion ratio, `toAmount` / `fromAmount`."""
  inverseRatio: NotRequired[str]
  """Inverse conversion ratio, `fromAmount` / `toAmount`."""
  createTime: NotRequired[int]
  """Millisecond epoch trade timestamp."""


class ConvertTradeFlow(TypedDict):
  """This account's Convert trade history within a time window."""

  list: NotRequired[list[ConvertTrade]]
  """Completed Convert trades."""
  startTime: NotRequired[int]
  """Echoed start of the queried window."""
  endTime: NotRequired[int]
  """Echoed end of the queried window."""
  limit: NotRequired[int]
  """Echoed record limit."""
  moreData: NotRequired[bool]
  """Whether more records exist past this page."""


class TradeFlow(RpcEndpoint):
  """Query this account's Convert trade history within a time window."""

  async def trade_flow(
    self,
    *,
    start_time: int,
    end_time: int,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> ConvertTradeFlow:
    """Query this account's Convert trade history within a time window.

    Args:
      start_time: Millisecond epoch start of the queried window.
      end_time: Millisecond epoch end of the queried window.
      limit: Number of records to return.

    References:
      - [Official docs](https://developers.binance.com/docs/convert/trade)
    """
    params: dict = {
      'startTime': start_time,
      'endTime': end_time,
    }
    if limit is not None:
      params['limit'] = limit
    _Response = ConvertTradeFlow
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/convert/tradeFlow',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def trade_flow_paged(
    self,
    *,
    start_time: int,
    end_time: int,
    limit: int | None = None,
    max_pages: int | None = None,
    allow_truncation: bool = False,
    validate: bool | None = None,
  ) -> AsyncIterator[ConvertTradeFlow]:
    """Yield successive pages of `trade_flow`.

    Moves the `start_time`–`end_time` window forwards by its own width and stops on the
    first empty window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `start_time` and `end_time` state, so
    choose a window the venue answers in one response — at most `limit` rows. A full
    page is evidence the window was capped, and raises `LogicError` rather than walking
    past the rows that were left out; pass `allow_truncation=True` to accept the loss
    and keep going.
    """
    lower = start_time
    upper = end_time
    width = upper - lower
    pages = 0
    while True:
      response = await self.trade_flow(
        start_time=lower, end_time=upper, limit=limit, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('list') if response is not None else None
      if not rows:
        break
      if not allow_truncation and len(rows) >= (limit if limit is not None else 100):
        raise LogicError(
          f'`trade_flow_paged` requested the window {lower} to {upper} and the venue returned a full page of {len(rows)} rows, so it may hold more; advancing would move past the rows that were left out. Narrow the window, or pass `allow_truncation=True` to accept the loss.'
        )
      lower = upper + 1
      upper = lower + width
