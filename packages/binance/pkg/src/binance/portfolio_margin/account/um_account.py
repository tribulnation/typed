from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmUmAccountDetailAssets(TypedDict):
  """PmUmAccountDetailAssets."""

  asset: NotRequired[str]
  """asset name."""
  crossWalletBalance: NotRequired[str]
  """wallet balance."""
  crossUnPnl: NotRequired[str]
  """unrealized profit."""
  maintMargin: NotRequired[str]
  """maintenance margin required."""
  initialMargin: NotRequired[str]
  """total initial margin required with current mark price."""
  positionInitialMargin: NotRequired[str]
  """initial margin required for positions with current mark price."""
  openOrderInitialMargin: NotRequired[str]
  """initial margin required for open orders with current mark price."""
  updateTime: NotRequired[Timestamp]
  """last update time."""


class PmUmAccountDetailPositions(TypedDict):
  """PmUmAccountDetailPositions."""

  symbol: NotRequired[str]
  """symbol name."""
  initialMargin: NotRequired[str]
  """total initial margin required with current mark price."""
  maintMargin: NotRequired[str]
  """maintenance margin required."""
  unrealizedProfit: NotRequired[str]
  """unrealized profit."""
  positionInitialMargin: NotRequired[str]
  """initial margin required for positions with current mark price."""
  openOrderInitialMargin: NotRequired[str]
  """initial margin required for open orders with current mark price."""
  leverage: NotRequired[str]
  """current initial leverage."""
  entryPrice: NotRequired[str]
  """average entry price."""
  maxNotional: NotRequired[str]
  """maximum available notional with current leverage."""
  bidNotional: NotRequired[str]
  """bids notional, ignore."""
  askNotional: NotRequired[str]
  """ask notional, ignore."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """position side."""
  positionAmt: NotRequired[str]
  """position amount."""
  updateTime: NotRequired[Timestamp]
  """last update time."""


class PmUmAccountDetail(TypedDict):
  """Get current UM account asset and position information."""

  assets: NotRequired[list[PmUmAccountDetailAssets]]
  """Assets."""
  positions: NotRequired[list[PmUmAccountDetailPositions]]
  """positions of all symbols in the market are returned."""


class UmAccount(RpcEndpoint):
  """Get UM Account Detail"""

  async def um_account(self, *, validate: bool | None = None) -> PmUmAccountDetail:
    """Get current UM account asset and position information.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-account-detail)
    """
    _Response = PmUmAccountDetail
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/papi/v1/um/account', validator=_validator, validate=validate
    )
