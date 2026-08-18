from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SymbolPriceTickerV20(TypedDict):
  """Latest price for one symbol (v2)."""

  symbol: str
  """Trading symbol."""
  price: str
  """Latest price."""
  time: int
  """Time this price was recorded, in milliseconds since epoch."""


class SymbolPriceTickerV2Item(TypedDict):
  """Latest price for one symbol (v2)."""

  symbol: str
  """Trading symbol."""
  price: str
  """Latest price."""
  time: int
  """Time this price was recorded, in milliseconds since epoch."""


class TickerPriceV2(RpcEndpoint):
  """Latest price for a symbol, or every symbol when omitted (v2)."""

  async def ticker_price_v2(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> SymbolPriceTickerV20 | list[SymbolPriceTickerV2Item]:
    """Latest price for a symbol, or every symbol when omitted (v2).

    Args:
      symbol: Trading symbol, e.g. BTCUSDT. Omit to get every symbol as an array.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#symbol-price-ticker-v2)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = SymbolPriceTickerV20 | list[SymbolPriceTickerV2Item]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.request(
      'GET',
      '/fapi/v2/ticker/price',
      params=params,
      validator=_validator,
      validate=validate,
    )
