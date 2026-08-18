"""`public/get_historical_volatility` — `public/get_historical_volatility`."""

from typing_extensions import Literal
from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_get_historical_volatility = validator[list[tuple[float, float]]](
  list[tuple[float, float]]
)


class GetHistoricalVolatility(RpcEndpoint):
  """`public/get_historical_volatility`."""

  async def get_historical_volatility(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    validate: bool | None = None,
  ) -> list[tuple[float, float]]:
    """Provides historical volatility data for a given cryptocurrency. Historical volatility measures the degree of price variation over a past period and is useful for risk assessment and option pricing.

    The response includes volatility statistics calculated from historical price movements. This data can be used for portfolio risk analysis and understanding market conditions.

    Args:
      currency: The currency symbol
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_historical_volatility)
    """
    params: dict = {
      'currency': currency,
    }
    return await self.request(
      'public/get_historical_volatility',
      params=params,
      validator=validate_get_historical_volatility,
      validate=validate,
    )
