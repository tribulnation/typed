"""`public/get_funding_rate_value` — `public/get_funding_rate_value`."""

from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_get_funding_rate_value = validator[float](float)


class GetFundingRateValue(RpcEndpoint):
  """`public/get_funding_rate_value`."""

  async def get_funding_rate_value(
    self,
    *,
    instrument_name: str,
    start_timestamp: int,
    end_timestamp: int,
    validate: bool | None = None,
  ) -> float:
    """Retrieves the funding rate (interest rate) value for a perpetual instrument over a specified time period. Funding rates are periodic payments exchanged between long and short positions in perpetual contracts.

    This method is applicable only for PERPETUAL instruments. The funding rate is typically expressed as a percentage and is used to keep the perpetual contract price aligned with the underlying index price.

    Args:
      instrument_name: Instrument name
      start_timestamp: The earliest timestamp to return result from (milliseconds since the UNIX epoch)
      end_timestamp: The most recent timestamp to return result from (milliseconds since the UNIX epoch)
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_funding_rate_value)
    """
    params: dict = {
      'instrument_name': instrument_name,
      'start_timestamp': start_timestamp,
      'end_timestamp': end_timestamp,
    }
    return await self.request(
      'public/get_funding_rate_value',
      params=params,
      validator=validate_get_funding_rate_value,
      validate=validate,
    )
