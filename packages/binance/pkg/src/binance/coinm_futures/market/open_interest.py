from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMOpenInterest(TypedDict):
  """Current open interest of a symbol."""

  symbol: str
  """Trading symbol."""
  pair: str
  """Underlying pair."""
  openInterest: str
  """Open interest, in contracts."""
  contractType: Literal[
    'PERPETUAL',
    'CURRENT_QUARTER',
    'NEXT_QUARTER',
    'CURRENT_QUARTER_DELIVERING',
    'NEXT_QUARTER_DELIVERING',
    'PERPETUAL_DELIVERING',
  ]
  """Contract type."""
  time: int
  """Time, in milliseconds since epoch."""


class OpenInterest(RpcEndpoint):
  """Present open interest of a specific symbol."""

  async def open_interest(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> CoinMOpenInterest:
    """Present open interest of a specific symbol.

    Args:
      symbol: Symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#open-interest)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = CoinMOpenInterest
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/dapi/v1/openInterest',
      params=params,
      validator=_validator,
      validate=validate,
    )
