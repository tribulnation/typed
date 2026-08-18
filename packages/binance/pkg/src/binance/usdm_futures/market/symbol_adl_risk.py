from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SymbolAdlRisk0(TypedDict):
  """ADL risk rating for one symbol."""

  symbol: str
  """Trading symbol."""
  adlRisk: Literal['LOW', 'MIDDLE', 'HIGH', 'EXTREMELY_HIGH']
  """ADL risk rating."""
  updateTime: int
  """Time this rating was last updated, in milliseconds since epoch."""


class SymbolAdlRiskItem(TypedDict):
  """ADL risk rating for one symbol."""

  symbol: str
  """Trading symbol."""
  adlRisk: Literal['LOW', 'MIDDLE', 'HIGH', 'EXTREMELY_HIGH']
  """ADL risk rating."""
  updateTime: int
  """Time this rating was last updated, in milliseconds since epoch."""


class SymbolAdlRisk(RpcEndpoint):
  """Symbol-level auto-deleveraging (ADL) risk rating. Measures the likelihood of ADL during liquidation, accounting for insurance fund balance, position concentration, order book depth, price volatility, average leverage, unrealized PnL, and margin utilization at the symbol level. Updated every 30 minutes."""

  async def symbol_adl_risk(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> SymbolAdlRisk0 | list[SymbolAdlRiskItem]:
    """Symbol-level auto-deleveraging (ADL) risk rating. Measures the likelihood of ADL during liquidation, accounting for insurance fund balance, position concentration, order book depth, price volatility, average leverage, unrealized PnL, and margin utilization at the symbol level. Updated every 30 minutes.

    Args:
      symbol: Trading symbol, e.g. BTCUSDT. Omit to get every symbol as an array.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#adl-risk)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = SymbolAdlRisk0 | list[SymbolAdlRiskItem]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.request(
      'GET',
      '/fapi/v1/symbolAdlRisk',
      params=params,
      validator=_validator,
      validate=validate,
    )
