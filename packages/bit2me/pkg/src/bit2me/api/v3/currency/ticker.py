from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Point(TypedDict):
  time: int
  """Unix timestamp in milliseconds for this data point."""
  price: str
  """Price at this point in time, as a decimal string, denominated in the request's `rateCurrency`."""
  interval: Literal['one_hour', 'one_day', 'one_week', 'one_month', 'one_year']
  """Time interval this data point represents, matching one of the requested `interval` values."""
  marketCap: NotRequired[str]
  """Market capitalization at this point in time, as a decimal string."""
  totalVolume: NotRequired[str]
  """Total trading volume at this point in time, as a decimal string."""
  fullyDilutedMarketCap: NotRequired[str]
  """Fully diluted market capitalization at this point in time, as a decimal string."""
  maxSupply: NotRequired[str]
  """Maximum possible supply of the cryptocurrency, as a decimal string."""
  totalSupply: NotRequired[str]
  """Circulating total supply of the cryptocurrency at this point in time, as a decimal string."""


validate_response = validator(dict[str, dict[str, list[Point]]])


class Ticker(RpcEndpoint):
  async def ticker(
    self,
    symbol: str,
    *,
    rate_currency: str | None = None,
    interval: list[Literal['one_hour', 'one_day', 'one_week', 'one_month', 'one_year']]
    | None = None,
    extended: bool | None = None,
    validate: bool | None = None,
  ) -> dict[str, dict[str, list[Point]]]:
    """Return ticker data for the selected cryptocurrency.

    Args:
      symbol: ISO 4217 cryptocurrency code to fetch ticker data for, e.g. `BTC`.
      rate_currency: Currency to express the ticker's price and market data in, as an ISO 4217 code.
      interval: Period(s) of time to fetch price/market data points for. Repeatable to request multiple intervals in one call.
      extended: Whether to include extended market data (market cap, volume, supply) alongside price. Defaults to `true`.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/market/GET/v3/currency/ticker/{symbol})
    """
    params = {}
    if rate_currency is not None:
      params['rateCurrency'] = rate_currency
    if interval is not None:
      params['interval'] = interval
    if extended is not None:
      params['extended'] = extended
    return await self.authed_request(
      'GET',
      f'/v3/currency/ticker/{symbol}',
      params=params,
      validator=validate_response,
      validate=validate,
    )
