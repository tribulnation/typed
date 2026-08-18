from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FuturesPositionRiskV2row(TypedDict):
  """A single symbol/position-side's current position information (v2)."""

  entryPrice: NotRequired[str]
  """Entry price."""
  breakEvenPrice: NotRequired[str]
  """Break-even price."""
  marginType: NotRequired[Literal['isolated', 'cross']]
  """Margin type for this position."""
  isAutoAddMargin: NotRequired[str]
  """Whether isolated margin auto-add is enabled."""
  isolatedMargin: NotRequired[str]
  """Isolated margin balance."""
  leverage: NotRequired[str]
  """Current leverage."""
  liquidationPrice: NotRequired[str]
  """Estimated liquidation price."""
  markPrice: NotRequired[str]
  """Current mark price."""
  maxNotionalValue: NotRequired[str]
  """Maximum notional value allowed at this leverage."""
  positionAmt: str
  """Position amount; positive for long, negative for short."""
  notional: NotRequired[str]
  """Notional value of the position."""
  isolatedWallet: NotRequired[str]
  """Isolated wallet balance backing this position."""
  symbol: str
  """Trading symbol."""
  unRealizedProfit: NotRequired[str]
  """Unrealized profit."""
  positionSide: Literal['BOTH', 'LONG', 'SHORT']
  """Position side."""
  updateTime: NotRequired[int]
  """Last update time, milliseconds since epoch."""


class PositionRiskV2(RpcEndpoint):
  """Get current position information (v2). Superseded by v3 for most accounts; kept for accounts that still route through v2. Use with the ACCOUNT_UPDATE user data stream event to meet timeliness/accuracy needs."""

  async def position_risk_v2(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[FuturesPositionRiskV2row]:
    """Get current position information (v2). Superseded by v3 for most accounts; kept for accounts that still route through v2. Use with the ACCOUNT_UPDATE user data stream event to meet timeliness/accuracy needs.

    Args:
      symbol: Trading symbol. If omitted, positions for every symbol are returned.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#position-information-v2)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = list[FuturesPositionRiskV2row]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/fapi/v2/positionRisk',
      params=params,
      validator=_validator,
      validate=validate,
    )
