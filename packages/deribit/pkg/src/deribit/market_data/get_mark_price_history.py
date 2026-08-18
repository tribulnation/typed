"""`public/get_mark_price_history` — `public/get_mark_price_history`."""

from typed_core.validation import validator
from deribit.core import RpcEndpoint
from typing_extensions import AsyncIterator

validate_get_mark_price_history = validator[list[tuple[float, float]]](
  list[tuple[float, float]]
)


class GetMarkPriceHistory(RpcEndpoint):
  """`public/get_mark_price_history`."""

  async def get_mark_price_history(
    self,
    *,
    instrument_name: str,
    start_timestamp: int,
    end_timestamp: int,
    validate: bool | None = None,
  ) -> list[tuple[float, float]]:
    """Retrieves 5-minute historical mark price data for an instrument. Mark prices are used for margin calculations and position valuations.

    **Note:** Currently, mark price history is available only for a subset of options that participate in volatility index calculations. All other instruments, including futures and perpetuals, will return an empty list.

    Args:
      instrument_name: Instrument name
      start_timestamp: The earliest timestamp to return result from (milliseconds since the UNIX epoch)
      end_timestamp: The most recent timestamp to return result from (milliseconds since the UNIX epoch)
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_mark_price_history)
    """
    params: dict = {
      'instrument_name': instrument_name,
      'start_timestamp': start_timestamp,
      'end_timestamp': end_timestamp,
    }
    return await self.request(
      'public/get_mark_price_history',
      params=params,
      validator=validate_get_mark_price_history,
      validate=validate,
    )

  async def get_mark_price_history_paged(
    self,
    *,
    instrument_name: str,
    start_timestamp: int,
    end_timestamp: int,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[tuple[float, float]]]:
    """Yield successive pages of `get_mark_price_history`.

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
      response = await self.get_mark_price_history(
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
