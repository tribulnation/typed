from typing_extensions import AsyncIterator, Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin
from typed_core.exceptions import LogicError


class FundingHistoryAction(TypedDict):
  type: Literal['fundingHistory']
  coin: str
  endTime: NotRequired[int]
  startTime: int


class FundingHistoryEvent(TypedDict):
  coin: str
  """Coin the funding event applies to."""
  fundingRate: str
  """Realized funding rate for the period, as a decimal string."""
  premium: str
  """Oracle-to-mark premium used to compute the funding rate, as a decimal string."""
  time: int
  """Event time, in milliseconds since epoch."""


adapter = pydantic.TypeAdapter(list[FundingHistoryEvent])


class FundingHistory(InfoMixin):
  async def funding_history(
    self,
    *,
    coin: str,
    end_time: int | None = None,
    start_time: int,
  ) -> list[FundingHistoryEvent]:
    """Retrieve historical hourly funding rate and premium events for a coin over a time range.

    Args:
      coin: Coin to fetch funding history for.
      end_time: End of the time range, in milliseconds since epoch, inclusive. Defaults to the current time.
      start_time: Start of the time range, in milliseconds since epoch, inclusive.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: FundingHistoryAction = {
      'type': 'fundingHistory',
      'coin': coin,
      'startTime': start_time,
    }
    if end_time is not None:
      params['endTime'] = end_time
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r

  async def funding_history_paged(
    self,
    *,
    coin: str,
    end_time: int | None = None,
    start_time: int,
    max_pages: int | None = None,
  ) -> AsyncIterator[list[FundingHistoryEvent]]:
    """Yield successive pages of `funding_history`.

    Passes the largest `time` seen so far back as `startTime` and stops on the first
    empty page, or after `max_pages` pages when one is given.

    Rows already yielded for that `time` value are dropped by position from the next
    page, so a value shared by more than one row is never duplicated or skipped. Raises
    `LogicError` if the venue's row order is not stable across requests, or if a full
    page of `500` rows shares one `time` value, since the rest of it would then be
    unreachable.
    """
    cursor: int = start_time
    overlap: list[FundingHistoryEvent] = []
    pages = 0
    while True:
      response = await self.funding_history(
        coin=coin, end_time=end_time, start_time=cursor
      )
      pages += 1
      if not response:
        break
      if response[: len(overlap)] != overlap:
        raise LogicError(
          f'`funding_history_paged` requested from {cursor} and the venue returned a different prefix than the previous page ended with; row order was expected to be stable across requests, so the walk stopped instead of dropping or duplicating rows.'
        )
      fresh = response[len(overlap) :]
      if fresh:
        yield fresh
      if max_pages is not None and pages >= max_pages:
        break
      values = [
        value
        for item in response
        if (value := (item.get('time') if item is not None else None)) is not None
      ]
      last = max(values) if values else None
      if last is not None and last > cursor:
        cursor = last
        overlap = [
          item
          for item in response
          if (item.get('time') if item is not None else None) == last
        ]
      elif len(response) >= 500:
        raise LogicError(
          f'`funding_history_paged` requested from {cursor} and the venue returned a full page of {len(response)} rows, all sharing `time` {cursor}; the rest of that value is unreachable and advancing would drop it.'
        )
      else:
        cursor += 1
        overlap = []
