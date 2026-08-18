from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmCmAccountDetailAssets(TypedDict):
  """PmCmAccountDetailAssets."""

  asset: NotRequired[str]
  """asset name."""
  crossWalletBalance: NotRequired[str]
  """total wallet balance."""
  crossUnPnl: NotRequired[str]
  """unrealized profit or loss."""
  maintMargin: NotRequired[str]
  """maintenance margin."""
  initialMargin: NotRequired[str]
  """total intial margin required with the latest mark price."""
  positionInitialMargin: NotRequired[str]
  """positions margin required with the latest mark price."""
  openOrderInitialMargin: NotRequired[str]
  """open orders intial margin required with the latest mark price."""
  updateTime: NotRequired[Timestamp]
  """last update time."""


class PmCmAccountDetailPositions(TypedDict):
  """PmCmAccountDetailPositions."""

  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  positionAmt: NotRequired[str]
  """position amount."""
  initialMargin: NotRequired[str]
  """total intial margin required with the latest mark price."""
  maintMargin: NotRequired[str]
  """maintenance margin."""
  unrealizedProfit: NotRequired[str]
  """unrealized profit."""
  positionInitialMargin: NotRequired[str]
  """positions margin required with the latest mark price."""
  openOrderInitialMargin: NotRequired[str]
  """open orders intial margin required with the latest mark price."""
  leverage: NotRequired[str]
  """current initial leverage."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """BOTH means that it is the position of One-way Mode."""
  entryPrice: NotRequired[str]
  """average entry price."""
  maxQty: NotRequired[str]
  """maximum quantity of base asset."""
  updateTime: NotRequired[Timestamp]
  """last update time."""


class PmCmAccountDetail(TypedDict):
  """Get current CM account asset and position information."""

  assets: NotRequired[list[PmCmAccountDetailAssets]]
  """Assets."""
  positions: NotRequired[list[PmCmAccountDetailPositions]]
  """positions of all symbols in the market are returned."""


class CmAccount(RpcEndpoint):
  """Get CM Account Detail"""

  async def cm_account(self, *, validate: bool | None = None) -> PmCmAccountDetail:
    """Get current CM account asset and position information.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-cm-account-detail)
    """
    _Response = PmCmAccountDetail
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/papi/v1/cm/account', validator=_validator, validate=validate
    )
