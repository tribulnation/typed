from decimal import Decimal
from datetime import datetime
from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Entry(TypedDict):
  id: NotRequired[str]
  """Market identifier"""
  symbol: NotRequired[str]
  """Market symbol"""
  minAmount: NotRequired[Decimal]
  """Minimum order amount (in terms of base currency)"""
  maxAmount: NotRequired[Decimal]
  """Maximum order amount (in terms of base currency)"""
  minPrice: NotRequired[Decimal]
  """Minimum order price (in terms of quote currency)"""
  maxPrice: NotRequired[Decimal]
  """Maximum order price (in terms of quote currency)"""
  minOrderSize: NotRequired[Decimal]
  """Minimum order size (in terms of base amount per quote price)"""
  pricePrecision: NotRequired[float]
  """Scaling decimals places for price"""
  tickSize: NotRequired[float]
  """Decimal number representing scaling decimals places for price"""
  amountPrecision: NotRequired[float]
  """Scaling decimals places for amount"""
  marketEnabled: NotRequired[Literal['enabled', 'enabled_at', 'frozen', 'disabled']]
  """The current status of the market. The market can be enabled, disabled, enabled at specified date in the `marketEnabledAt` field, or frozen, which does not allow orders to be added or deleted"""
  marketEnabledAt: NotRequired[datetime | None]
  """Date time in ISO 8601 string format"""
  initialPrice: NotRequired[Decimal]
  """Initial market price. If the market is not yet enabled, the orders must take that reference price to be placed above or below"""


validate_response = validator(list[Entry])


class Markets(RpcEndpoint):
  async def __call__(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[Entry]:
    """Get a list of markets (quantity and price precisions, order minimums and maximums, status).

    Args:
      symbol: The market symbol to filter (optional, by default returns all markets)
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/marketdata/GET/v1/trading/market-config)
    """
    params = {'symbol': symbol} if symbol is not None else None
    return await self.request(
      'GET',
      '/v1/trading/market-config',
      params=params,
      validator=validate_response,
      validate=validate,
    )
