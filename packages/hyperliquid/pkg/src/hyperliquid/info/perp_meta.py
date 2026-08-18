from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class PerpMarginTier(TypedDict):
  lowerBound: str
  """Position notional value (USD) at or above which this tier's `maxLeverage` applies."""
  maxLeverage: int
  """Maximum leverage allowed for position notional at or above `lowerBound`."""


class PerpMetaAction(TypedDict):
  type: Literal['meta']
  dex: NotRequired[str]


class PerpUniverseAsset(TypedDict):
  isDelisted: NotRequired[bool]
  """Whether this asset has been delisted; delisted assets no longer accept new positions."""
  marginMode: NotRequired[Literal['strictIsolated', 'noCross', 'normal']]
  """Margin mode restriction for this asset. `strictIsolated` forbids removing margin from an open isolated position; `noCross` allows isolated margin only, never cross; `normal` places no restriction beyond the account's own margin mode choice."""
  marginTableId: NotRequired[int]
  """Identifier of this asset's entry in `marginTables`."""
  maxLeverage: int
  """Maximum leverage a position in this asset may use."""
  name: str
  """Asset symbol (e.g. "BTC"), unique within this dex's universe."""
  onlyIsolated: NotRequired[bool]
  """Whether this asset can only be traded with isolated margin."""
  szDecimals: int
  """Number of decimal places order sizes for this asset are rounded to."""


class PerpMarginTable(TypedDict):
  description: str
  """Human-readable label for this margin table (e.g. "tiered 10x"); empty string when the table carries no label."""
  marginTiers: list[PerpMarginTier]
  """Leverage tiers for this table, in ascending order of `lowerBound`."""


class PerpDexMeta(TypedDict):
  """Universe and margin-table metadata for one perpetuals dex."""

  collateralToken: NotRequired[int]
  """Spot token index used as this perp dex's collateral currency (0 is USDC, the collateral for Hyperliquid's own perp dex)."""
  marginTables: list[tuple[int, PerpMarginTable]]
  """Every margin table referenced by `universe[].marginTableId`, as `[id, table]` pairs."""
  universe: list[PerpUniverseAsset]
  """Perpetual assets listed on this dex, in the same order as their on-chain asset index."""


adapter = pydantic.TypeAdapter(PerpDexMeta)


class PerpMeta(InfoMixin):
  async def perp_meta(self, *, dex: str | None = None) -> PerpDexMeta:
    """Retrieve the trading universe and margin tables for a perpetuals dex: every listed asset's size precision, max leverage, and margin table assignment, plus each referenced margin table's tiered leverage schedule.

    Args:
      dex: Perp dex name. Empty string (the default) selects Hyperliquid's own perp dex; a HIP-3 builder-deployed dex is selected by its own name.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: PerpMetaAction = {
      'type': 'meta',
    }
    if dex is not None:
      params['dex'] = dex
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
