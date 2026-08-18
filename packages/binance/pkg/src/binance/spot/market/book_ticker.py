from json import dumps
from typing_extensions import Literal
from typed_core.validation import validator
from binance.types import BookTicker
from binance.core.endpoint.rpc import RpcEndpoint


class BookTickerEndpoint(RpcEndpoint):
  """Symbol order book ticker"""

  async def book_ticker(
    self,
    *,
    symbol: str | None = None,
    symbols: list[str] | None = None,
    symbol_status: Literal['TRADING', 'HALT', 'BREAK'] | None = None,
    validate: bool | None = None,
  ) -> BookTicker | list[BookTicker]:
    """Best price/quantity on the order book for a symbol or symbols.

    Args:
      symbol: Single symbol to query. Cannot be combined with `symbols`. If neither `symbol` nor `symbols` is sent, book tickers for all symbols are returned as an array.
      symbols: Symbols to query, e.g. ["BTCUSDT","BNBUSDT"]. Cannot be combined with `symbol`.
      symbol_status: Filter for symbols with this trading status. For a single symbol, a status mismatch returns error -1220 SYMBOL_DOES_NOT_MATCH_STATUS; for multiple or all symbols, non-matching ones are simply excluded from the response.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#symbol-order-book-ticker)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if symbols is not None:
      params['symbols'] = dumps(symbols, separators=(',', ':'))
    if symbol_status is not None:
      params['symbolStatus'] = symbol_status
    _Response = BookTicker | list[BookTicker]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.request(
      'GET',
      '/api/v3/ticker/bookTicker',
      params=params,
      validator=_validator,
      validate=validate,
    )
