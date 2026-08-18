from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class UsdMWsBookTicker0(TypedDict):
  """Best bid/ask price and quantity for one symbol."""

  lastUpdateId: int
  """Identifier of the last order-book update reflected in this quote."""
  symbol: str
  """Trading symbol."""
  bidPrice: str
  """Best bid price."""
  bidQty: str
  """Quantity available at the best bid."""
  askPrice: str
  """Best ask price."""
  askQty: str
  """Quantity available at the best ask."""
  time: int
  """Time this quote was recorded, in milliseconds since epoch."""


class UsdMWsBookTickerItem(TypedDict):
  """Best bid/ask price and quantity for one symbol."""

  lastUpdateId: int
  """Identifier of the last order-book update reflected in this quote."""
  symbol: str
  """Trading symbol."""
  bidPrice: str
  """Best bid price."""
  bidQty: str
  """Quantity available at the best bid."""
  askPrice: str
  """Best ask price."""
  askQty: str
  """Quantity available at the best ask."""
  time: int
  """Time this quote was recorded, in milliseconds since epoch."""


class TickerBook(WsRpcEndpoint):
  """Best bid/ask price and quantity for a symbol, or every symbol when omitted."""

  async def ticker_book(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> UsdMWsBookTicker0 | list[UsdMWsBookTickerItem]:
    """Best bid/ask price and quantity for a symbol, or every symbol when omitted.

    Args:
      symbol: Trading symbol, e.g. BTCUSDT. Omit to get every symbol as an array.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-api/market-data#symbol-order-book-ticker)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = UsdMWsBookTicker0 | list[UsdMWsBookTickerItem]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.request(
      'ticker.book', params=params, validator=_validator, validate=validate
    )
