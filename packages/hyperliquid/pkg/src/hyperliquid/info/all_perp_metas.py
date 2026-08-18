from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class AllPerpMetasAction(TypedDict):
  type: Literal['allPerpMetas']


class PerpMarginTier(TypedDict):
  lowerBound: str
  """Position notional value (USD) at or above which this tier's `maxLeverage` applies."""
  maxLeverage: int
  """Maximum leverage allowed for position notional at or above `lowerBound`."""


class PerpUniverseAsset(TypedDict):
  growthMode: NotRequired[Literal['enabled']]
  """Present and set to "enabled" when this asset participates in the HIP-3 growth-mode fee schedule (`SetGrowthModes`); omitted otherwise."""
  isDelisted: NotRequired[bool]
  """Whether this asset has been delisted; delisted assets no longer accept new positions."""
  lastGrowthModeChangeTime: NotRequired[str]
  """ISO-8601 timestamp of the most recent `growthMode` change for this asset."""
  marginMode: NotRequired[Literal['strictIsolated', 'noCross', 'normal']]
  """Margin mode restriction for this asset. `strictIsolated` forbids removing margin from an open isolated position; `noCross` allows isolated margin only, never cross; `normal` places no restriction beyond the account's own margin mode choice."""
  marginTableId: int
  """Identifier of this asset's entry in `marginTables`."""
  maxLeverage: int
  """Maximum leverage a position in this asset may use."""
  name: str
  """Asset symbol, unique within this dex's universe. HIP-3 dex assets are commonly prefixed with the dex name (e.g. "felix:TSLA")."""
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
  collateralToken: int
  """Spot token index used as this perp dex's collateral currency (0 is USDC, the collateral for Hyperliquid's own perp dex)."""
  marginTables: list[tuple[int, PerpMarginTable]]
  """Every margin table referenced by `universe[].marginTableId`, as `[id, table]` pairs."""
  universe: list[PerpUniverseAsset]
  """Perpetual assets listed on this dex, in the same order as their on-chain asset index."""


adapter = pydantic.TypeAdapter(list[PerpDexMeta])


class AllPerpMetas(InfoMixin):
  async def all_perp_metas(self) -> list[PerpDexMeta]:
    """Retrieve universe and margin-table metadata for every perpetuals dex on the venue at once: Hyperliquid's own dex plus every HIP-3 builder-deployed dex, one entry per dex.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: AllPerpMetasAction = {
      'type': 'allPerpMetas',
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
