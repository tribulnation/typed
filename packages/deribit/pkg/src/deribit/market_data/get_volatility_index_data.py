"""`public/get_volatility_index_data` — `public/get_volatility_index_data`."""

from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class VolatilityIndexData(TypedDict):
  """A page of volatility index candles."""

  data: NotRequired[list[tuple[int, float, float, float, float]]]
  """Candles for this page, ascending by timestamp."""
  continuation: NotRequired[int | None]
  """Continuation cursor -- `null` once the requested range is fully covered."""


validate_get_volatility_index_data = validator[VolatilityIndexData](VolatilityIndexData)


class GetVolatilityIndexData(RpcEndpoint):
  """`public/get_volatility_index_data`."""

  async def get_volatility_index_data(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    start_timestamp: int,
    end_timestamp: int,
    resolution: Literal['1', '60', '3600', '43200', '1D'],
    validate: bool | None = None,
  ) -> VolatilityIndexData:
    """Retrieves volatility index (VIX) chart data formatted as candles. Volatility indexes measure market expectations of future volatility and are useful for risk assessment and trading strategies.

    Use the `vix_resolution` parameter to specify the candle interval. The data shows historical volatility index values over time and is formatted for use in charting applications.

    Args:
      currency: The currency symbol
      start_timestamp: The earliest timestamp to return result from (milliseconds since the UNIX epoch)
      end_timestamp: The most recent timestamp to return result from (milliseconds since the UNIX epoch)
      resolution: Time resolution given in full seconds or keyword `1D` (only some specific resolutions are supported). The wire value is a string (`"3600"`, per this endpoint's own live-captured `examples/01.request.json`), not a bare number -- the enum entries were previously typed as JSON numbers, contradicting the parameter's own declared `type: string` and rejecting the recorded example.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_volatility_index_data)
    """
    params: dict = {
      'currency': currency,
      'start_timestamp': start_timestamp,
      'end_timestamp': end_timestamp,
      'resolution': resolution,
    }
    return await self.request(
      'public/get_volatility_index_data',
      params=params,
      validator=validate_get_volatility_index_data,
      validate=validate,
    )

  async def get_volatility_index_data_paged(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    start_timestamp: int,
    end_timestamp: int,
    resolution: Literal['1', '60', '3600', '43200', '1D'],
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[VolatilityIndexData]:
    """Yield successive pages of `get_volatility_index_data`.

    Passes each page's token back as `end_timestamp` and stops when a response carries
    no `continuation`, or after `max_pages` pages when one is given.
    """
    end_timestamp_cursor: int | None = end_timestamp
    pages = 0
    while True:
      response = await self.get_volatility_index_data(
        currency=currency,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp_cursor,
        resolution=resolution,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      end_timestamp_cursor = (
        response.get('continuation') if response is not None else None
      )
      if not end_timestamp_cursor:
        break
