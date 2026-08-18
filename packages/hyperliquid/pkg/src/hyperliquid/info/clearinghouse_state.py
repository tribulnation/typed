from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class ClearinghouseStateAction(TypedDict):
  type: Literal['clearinghouseState']
  user: str
  dex: NotRequired[str]


class CrossLeverage(TypedDict):
  """Leverage for a cross-margined position."""

  type: Literal['cross']
  """Margin mode."""
  value: int
  """Leverage multiplier."""


class CrossMarginSummary(TypedDict):
  """Margin summary scoped to cross-margined positions."""

  accountValue: str
  """Total account value backing cross-margined positions."""
  totalMarginUsed: str
  """Total margin currently used by cross-margined positions."""
  totalNtlPos: str
  """Total notional value of cross-margined positions."""
  totalRawUsd: str
  """Total raw USD value backing cross-margined positions."""


class CumulativeFunding(TypedDict):
  """Cumulative funding paid (positive) or received (negative) by the position, tracked over three windows."""

  allTime: str
  """Cumulative funding since the asset was listed."""
  sinceChange: str
  """Cumulative funding since the position size last changed."""
  sinceOpen: str
  """Cumulative funding since the position was opened."""


class IsolatedLeverage(TypedDict):
  """Leverage for an isolated-margin position."""

  type: Literal['isolated']
  """Margin mode."""
  value: int
  """Leverage multiplier."""
  rawUsd: str
  """USD margin allocated to the isolated position, before unrealized PnL."""


class MarginSummary(TypedDict):
  """Margin summary across the whole account (cross and isolated positions together)."""

  accountValue: str
  """Total account value across all positions and balance."""
  totalMarginUsed: str
  """Total margin currently used across all positions."""
  totalNtlPos: str
  """Total notional value of all open positions."""
  totalRawUsd: str
  """Total raw USD value backing the account."""


class PerpPosition(TypedDict):
  """The details of the open position."""

  coin: str
  """Perpetual asset symbol, e.g. "ETH"."""
  cumFunding: CumulativeFunding
  entryPx: str
  """Volume-weighted average entry price of the position."""
  leverage: CrossLeverage | IsolatedLeverage
  """The position's leverage settings. Cross-margined positions share account-wide margin; isolated positions carry their own dedicated margin, reported as `rawUsd`."""
  liquidationPx: str
  """Estimated liquidation price for the position."""
  marginUsed: str
  """Margin currently allocated to the position."""
  maxLeverage: int
  """Maximum leverage allowed for this asset at the account's current settings."""
  positionValue: str
  """Notional value of the position, in USD."""
  returnOnEquity: str
  """Position return on equity, as a decimal fraction."""
  szi: str
  """Signed position size: positive for long, negative for short."""
  unrealizedPnl: str
  """Unrealized profit or loss on the position."""


class AssetPosition(TypedDict):
  """A single open perpetual position."""

  position: PerpPosition
  type: Literal['oneWay']
  """Position mode. Hyperliquid currently supports only one-way (non-hedge) positions."""


class ClearinghouseState(TypedDict):
  assetPositions: list[AssetPosition]
  """The user's open perpetual positions."""
  crossMaintenanceMarginUsed: str
  """Maintenance margin currently used by cross-margined positions."""
  crossMarginSummary: CrossMarginSummary
  marginSummary: MarginSummary
  time: int
  """Server time the snapshot was taken, in Unix epoch milliseconds."""
  withdrawable: str
  """Amount available to withdraw, after margin requirements."""


adapter = pydantic.TypeAdapter(ClearinghouseState)


class ClearinghouseStateEndpoint(InfoMixin):
  async def clearinghouse_state(
    self,
    *,
    user: str,
    dex: str | None = None,
  ) -> ClearinghouseState:
    """Retrieve a user's open perpetual positions, margin usage, and withdrawable balance through Hyperliquid POST /info using request type `clearinghouseState`.

    Args:
      user: Onchain address in 42-character hexadecimal format, e.g. 0x0000000000000000000000000000000000000000.
      dex: Perp dex name. Defaults to the empty string, which represents the first perp dex.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: ClearinghouseStateAction = {
      'type': 'clearinghouseState',
      'user': user,
    }
    if dex is not None:
      params['dex'] = dex
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
