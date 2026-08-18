from typing_extensions import NotRequired, TypedDict
from mexc.spot.core import ErrorResponse, SpotMixin
from mexc.core import validator

class TickerPrice(TypedDict):
  """Latest price ticker."""
  symbol: str
  """Spot symbol."""
  price: str
  """Latest traded price."""

class TickerPriceListItem(TypedDict):
  """Latest price ticker."""
  symbol: NotRequired[str]
  """Spot symbol."""
  price: NotRequired[str]
  """Latest traded price."""

Response: type[TickerPrice | list[TickerPriceListItem] | ErrorResponse] = TickerPrice | list[TickerPriceListItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class TickerPriceEndpoint(SpotMixin):
  async def ticker_price(
    self, *,
    symbol: str | None = None, validate: bool | None = None,
  ) -> TickerPrice | list[TickerPriceListItem]:
    """Return latest price for one spot symbol or all symbols.

    Args:
      symbol: Spot symbol. If omitted, returns all symbols.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#symbol-price-ticker)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    r = await self.request('GET', '/api/v3/ticker/price', params=params)
    return self.output(r.text, adapter, validate)
