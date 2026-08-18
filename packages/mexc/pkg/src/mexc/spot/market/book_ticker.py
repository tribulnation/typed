from typing_extensions import NotRequired, TypedDict
from mexc.spot.core import ErrorResponse, SpotMixin
from mexc.core import validator

class BookTicker(TypedDict):
  """Best bid and ask ticker."""
  symbol: str
  """Spot symbol."""
  bidPrice: str | None
  """Best bid price. Null when the symbol has no resting order on that side."""
  bidQty: str | None
  """Best bid quantity. Null when the symbol has no resting order on that side."""
  askPrice: str | None
  """Best ask price. Null when the symbol has no resting order on that side."""
  askQty: str | None
  """Best ask quantity. Null when the symbol has no resting order on that side."""

class BookTickerListItem(TypedDict):
  """Best bid and ask ticker."""
  symbol: NotRequired[str]
  """Spot symbol."""
  bidPrice: NotRequired[str | None]
  """Best bid price. Null when the symbol has no resting order on that side."""
  bidQty: NotRequired[str | None]
  """Best bid quantity. Null when the symbol has no resting order on that side."""
  askPrice: NotRequired[str | None]
  """Best ask price. Null when the symbol has no resting order on that side."""
  askQty: NotRequired[str | None]
  """Best ask quantity. Null when the symbol has no resting order on that side."""

Response: type[BookTicker | list[BookTickerListItem] | ErrorResponse] = BookTicker | list[BookTickerListItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class BookTickerEndpoint(SpotMixin):
  async def book_ticker(
    self, *,
    symbol: str | None = None, validate: bool | None = None,
  ) -> BookTicker | list[BookTickerListItem]:
    """Return best bid and ask for one spot symbol or all symbols.

    Args:
      symbol: Spot symbol. If omitted, returns all symbols.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#symbol-order-book-ticker)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    r = await self.request('GET', '/api/v3/ticker/bookTicker', params=params)
    return self.output(r.text, adapter, validate)
