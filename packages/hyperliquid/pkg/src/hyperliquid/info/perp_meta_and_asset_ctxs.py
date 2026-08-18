from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class PerpAssetContext(TypedDict):
  dayBaseVlm: NotRequired[str]
  """Trailing 24h trading volume for this asset, denominated in the base asset."""
  dayNtlVlm: str
  """Trailing 24h trading volume for this asset, denominated in USD notional."""
  funding: str
  """Current hourly funding rate for this asset."""
  impactPxs: list[str] | None
  """Bid/ask impact prices (`[impactBid, impactAsk]`) used to compute the impact mid price; null when the order book has no impact-eligible liquidity."""
  markPx: str
  """Current mark price used for margin and liquidation calculations."""
  midPx: None | str
  """Current best-bid/best-ask midpoint price; null when the order book is empty on either side."""
  openInterest: str
  """Current total open interest for this asset, denominated in the base asset."""
  oraclePx: str
  """Current oracle price for this asset."""
  premium: None | str
  """Current premium of mark price over oracle price, as a fraction; null when it cannot be computed (e.g. no impact-eligible liquidity)."""
  prevDayPx: str
  """Mark price 24h ago, used to compute daily price change."""


class PerpMarginTier(TypedDict):
  lowerBound: str
  """Position notional value (USD) at or above which this tier's `maxLeverage` applies."""
  maxLeverage: int
  """Maximum leverage allowed for position notional at or above `lowerBound`."""


class PerpMetaAndAssetCtxsAction(TypedDict):
  type: Literal['metaAndAssetCtxs']
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
  collateralToken: int
  """Spot token index used as this perp dex's collateral currency (0 is USDC, the collateral for Hyperliquid's own perp dex)."""
  marginTables: list[tuple[int, PerpMarginTable]]
  """Every margin table referenced by `universe[].marginTableId`, as `[id, table]` pairs."""
  universe: list[PerpUniverseAsset]
  """Perpetual assets listed on this dex, in the same order as their on-chain asset index."""


adapter = pydantic.TypeAdapter(tuple[PerpDexMeta, list[PerpAssetContext]])


class PerpMetaAndAssetCtxs(InfoMixin):
  async def perp_meta_and_asset_ctxs(
    self,
    *,
    dex: str | None = None,
  ) -> tuple[PerpDexMeta, list[PerpAssetContext]]:
    """Retrieve a perpetuals dex's universe/margin-table metadata together with each listed asset's current market context (mark/mid/oracle price, funding, open interest, volume) in one call.

    Args:
      dex: Perp dex name. Empty string (the default) selects Hyperliquid's own perp dex; a HIP-3 builder-deployed dex is selected by its own name.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: PerpMetaAndAssetCtxsAction = {
      'type': 'metaAndAssetCtxs',
    }
    if dex is not None:
      params['dex'] = dex
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
