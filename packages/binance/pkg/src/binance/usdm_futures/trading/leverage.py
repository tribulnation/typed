from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LeverageChange(TypedDict):
  """Result of changing a symbol's initial leverage."""

  leverage: int
  """New initial leverage."""
  maxNotionalValue: NotRequired[str]
  """Maximum notional value allowed at this leverage."""
  symbol: str
  """Trading symbol."""


class Leverage(RpcEndpoint):
  """Change user's initial leverage for a specific symbol market."""

  async def leverage(
    self,
    *,
    symbol: str,
    leverage: int,
    validate: bool | None = None,
  ) -> LeverageChange:
    """Change user's initial leverage for a specific symbol market.

    Args:
      symbol: Trading symbol, e.g. BTCUSDT.
      leverage: Target initial leverage, range depends on the symbol's leverage brackets.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#change-initial-leverage)
    """
    params: dict = {
      'symbol': symbol,
      'leverage': leverage,
    }
    _Response = LeverageChange
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/fapi/v1/leverage',
      params=params,
      validator=_validator,
      validate=validate,
    )
