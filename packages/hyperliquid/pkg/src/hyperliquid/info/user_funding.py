from typing_extensions import AsyncIterator, Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin
from typed_core.exceptions import LogicError


class FundingDelta(TypedDict):
  """A single funding payment applied to a user's position."""

  type: Literal['funding']
  """Ledger delta discriminator for a funding payment."""
  coin: str
  """Perp coin the funding payment applies to. A HIP-3 perp is prefixed with its dex name, e.g. `xyz:XYZ100`."""
  usdc: str
  """Funding paid (negative) or received (positive), in USDC, as a decimal string."""
  szi: str
  """Signed size of the funded position, in base units, as a decimal string."""
  fundingRate: str
  """Funding rate applied for the period, as a decimal string (e.g. `0.0000417` = 0.00417%)."""
  nSamples: int | None
  """Number of samples the funding rate was averaged over, or `null` when not applicable."""


class UserFundingAction(TypedDict):
  type: Literal['userFunding']
  user: str
  startTime: int
  endTime: NotRequired[int]


class UserFundingEntry(TypedDict):
  """A single funding payment entry in the user's history."""

  delta: FundingDelta
  hash: str
  """Hash of the block that applied the funding payment."""
  time: int
  """Time the funding payment was applied, in milliseconds since epoch."""


adapter = pydantic.TypeAdapter(list[UserFundingEntry])


class UserFunding(InfoMixin):
  async def user_funding(
    self,
    *,
    user: str,
    start_time: int,
    end_time: int | None = None,
  ) -> list[UserFundingEntry]:
    """Retrieve a user's funding payment history within a time range. Responses that take a time range return at most 500 elements or distinct blocks of data; to query a larger range, repeat the call using the last returned entry's `time` as the next `start_time`.

    Args:
      user: Account address to query, in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000. Must be the actual account address of the master or sub-account being queried -- an agent wallet's address returns an empty result.
      start_time: Start of the time range, in milliseconds since epoch, inclusive.
      end_time: End of the time range, in milliseconds since epoch, inclusive. Defaults to the current time.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals)
    """
    params: UserFundingAction = {
      'type': 'userFunding',
      'user': user,
      'startTime': start_time,
    }
    if end_time is not None:
      params['endTime'] = end_time
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r

  async def user_funding_paged(
    self,
    *,
    user: str,
    start_time: int,
    end_time: int | None = None,
    max_pages: int | None = None,
  ) -> AsyncIterator[list[UserFundingEntry]]:
    """Yield successive pages of `user_funding`.

    Passes the largest `time` seen so far back as `startTime` and stops on the first
    empty page, or after `max_pages` pages when one is given.

    Rows already yielded for that `time` value are dropped by position from the next
    page, so a value shared by more than one row is never duplicated or skipped. Raises
    `LogicError` if the venue's row order is not stable across requests, or if a full
    page of `500` rows shares one `time` value, since the rest of it would then be
    unreachable.
    """
    cursor: int = start_time
    overlap: list[UserFundingEntry] = []
    pages = 0
    while True:
      response = await self.user_funding(
        user=user, start_time=cursor, end_time=end_time
      )
      pages += 1
      if not response:
        break
      if response[: len(overlap)] != overlap:
        raise LogicError(
          f'`user_funding_paged` requested from {cursor} and the venue returned a different prefix than the previous page ended with; row order was expected to be stable across requests, so the walk stopped instead of dropping or duplicating rows.'
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
          f'`user_funding_paged` requested from {cursor} and the venue returned a full page of {len(response)} rows, all sharing `time` {cursor}; the rest of that value is unreachable and advancing would drop it.'
        )
      else:
        cursor += 1
        overlap = []
