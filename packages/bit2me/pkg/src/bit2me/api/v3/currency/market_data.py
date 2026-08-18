from typing_extensions import TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class CurrencyMarketDataV3response(TypedDict):
  marketCap: str
  """Total market capitalization of the currency, as a decimal string, in USD."""
  totalVolume: str
  """Total 24-hour trading volume of the currency, as a decimal string, in USD."""
  fullyDilutedMarketCap: str
  """Market capitalization computed against the currency's max supply rather than its circulating supply, as a decimal string, in USD."""
  maxSupply: int
  """Maximum possible supply of the currency that will ever exist."""
  totalSupply: int
  """Circulating total supply of the currency."""


validate_response = validator(CurrencyMarketDataV3response)


class MarketData(RpcEndpoint):
  async def market_data(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> CurrencyMarketDataV3response:
    """Returns the market data for given currency in USD

    Args:
      symbol: ISO 4217 cryptocurrency code to fetch market data for, e.g. `BTC`.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/market/GET/v3/currency/market-data/{symbol})
    """
    return await self.authed_request(
      'GET',
      f'/v3/currency/market-data/{symbol}',
      validator=validate_response,
      validate=validate,
    )
