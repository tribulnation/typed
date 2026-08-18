"""`public/get_funding_rate_history` — `public/get_funding_rate_history`."""

from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class FundingRatePointItem(TypedDict):
  """Hourly funding rate data for one hour."""

  timestamp: NotRequired[int]
  """The timestamp (milliseconds since the Unix epoch)"""
  prev_index_price: NotRequired[float]
  """Price in base currency"""
  index_price: NotRequired[float]
  """Price in base currency"""
  interest_1h: NotRequired[float]
  """1hour interest rate"""
  interest_8h: NotRequired[float]
  """8hour interest rate"""


validate_get_funding_rate_history = validator[list[FundingRatePointItem]](
  list[FundingRatePointItem]
)


class GetFundingRateHistory(RpcEndpoint):
  """`public/get_funding_rate_history`."""

  async def get_funding_rate_history(
    self,
    *,
    instrument_name: str,
    start_timestamp: int,
    end_timestamp: int,
    validate: bool | None = None,
  ) -> list[FundingRatePointItem]:
    """Retrieves hourly historical funding rate (interest rate) data for a PERPETUAL instrument over a specified time period. Funding rates are periodic payments exchanged between long and short positions in perpetual contracts.

    The response includes hourly funding rate values, which can be used to analyze funding rate trends and calculate historical funding costs. This method is applicable only for PERPETUAL instruments.

    Args:
      instrument_name: Instrument name
      start_timestamp: The earliest timestamp to return result from (milliseconds since the UNIX epoch)
      end_timestamp: The most recent timestamp to return result from (milliseconds since the UNIX epoch)
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_funding_rate_history)
    """
    params: dict = {
      'instrument_name': instrument_name,
      'start_timestamp': start_timestamp,
      'end_timestamp': end_timestamp,
    }
    return await self.request(
      'public/get_funding_rate_history',
      params=params,
      validator=validate_get_funding_rate_history,
      validate=validate,
    )

  async def get_funding_rate_history_paged(
    self,
    *,
    instrument_name: str,
    start_timestamp: int,
    end_timestamp: int,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[FundingRatePointItem]]:
    """Yield successive pages of `get_funding_rate_history`.

    Moves the `start_timestamp`–`end_timestamp` window forwards by its own width and
    stops on the first empty window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `start_timestamp` and `end_timestamp`
    state, so choose a window the venue answers in one response: it caps a wider one,
    and the walk moves past the rows that were left out.
    """
    lower = start_timestamp
    upper = end_timestamp
    width = upper - lower
    pages = 0
    while True:
      response = await self.get_funding_rate_history(
        instrument_name=instrument_name,
        start_timestamp=lower,
        end_timestamp=upper,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      if not response:
        break
      lower = upper
      upper = lower + width
