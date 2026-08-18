from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmUmPositionInformation(TypedDict):
  """PmUmPositionInformation."""

  entryPrice: NotRequired[str]
  """average entry price."""
  leverage: NotRequired[str]
  """current initial leverage."""
  markPrice: NotRequired[str]
  """Mark Price."""
  maxNotionalValue: NotRequired[str]
  """Max Notional Value."""
  positionAmt: NotRequired[str]
  """position amount."""
  notional: NotRequired[str]
  """Notional."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  unRealizedProfit: NotRequired[str]
  """Un Realized Profit."""
  liquidationPrice: NotRequired[str]
  """Liquidation Price."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """BOTH means that it is the position of One-way Mode."""
  updateTime: NotRequired[Timestamp]
  """last update time."""


class UmPositionRisk(RpcEndpoint):
  """Query UM Position Information"""

  async def um_position_risk(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[PmUmPositionInformation]:
    """Get current UM position information.

    Args:
      symbol: Trading pair symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-um-position-information)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = list[PmUmPositionInformation]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/um/positionRisk',
      params=params,
      validator=_validator,
      validate=validate,
    )
