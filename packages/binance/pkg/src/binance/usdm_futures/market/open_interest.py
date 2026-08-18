from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class OpenInterest(TypedDict):
  """Present open interest for a symbol."""

  openInterest: str
  """Amount of outstanding contracts not yet settled."""
  symbol: str
  """Trading symbol."""
  time: int
  """Transaction time, in milliseconds since epoch."""


class OpenInterestEndpoint(RpcEndpoint):
  """Present open interest for a symbol."""

  async def open_interest(
    self, *, symbol: str, validate: bool | None = None
  ) -> OpenInterest:
    """Present open interest for a symbol.

    Args:
      symbol: Trading symbol, e.g. BTCUSDT.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#open-interest)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = OpenInterest
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/fapi/v1/openInterest',
      params=params,
      validator=_validator,
      validate=validate,
    )
