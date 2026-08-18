from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class UsdMWsSymbolPrice0(TypedDict):
  """Latest price for one symbol."""

  symbol: str
  """Trading symbol."""
  price: str
  """Latest price."""
  time: int
  """Time this price was recorded, in milliseconds since epoch."""


class UsdMWsSymbolPriceItem(TypedDict):
  """Latest price for one symbol."""

  symbol: str
  """Trading symbol."""
  price: str
  """Latest price."""
  time: int
  """Time this price was recorded, in milliseconds since epoch."""


class TickerPrice(WsRpcEndpoint):
  """Latest price for a symbol, or every symbol when omitted."""

  async def ticker_price(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> UsdMWsSymbolPrice0 | list[UsdMWsSymbolPriceItem]:
    """Latest price for a symbol, or every symbol when omitted.

    Args:
      symbol: Trading symbol, e.g. BTCUSDT. Omit to get every symbol as an array.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-api/market-data#symbol-price-ticker)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = UsdMWsSymbolPrice0 | list[UsdMWsSymbolPriceItem]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.request(
      'ticker.price', params=params, validator=_validator, validate=validate
    )
