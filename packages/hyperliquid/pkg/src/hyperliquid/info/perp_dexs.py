from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class PerpDex(TypedDict):
  """A builder-deployed (HIP-3) perp dex's metadata and per-coin overrides."""

  assetToFundingInterestRate: NotRequired[list[tuple[str, str]]]
  """Per-coin funding interest rate overrides, as `[coin, rate]` pairs."""
  assetToFundingMultiplier: list[tuple[str, str]]
  """Per-coin funding rate multiplier overrides, as `[coin, multiplier]` pairs."""
  assetToStreamingOiCap: list[tuple[str, str]]
  """Per-coin streaming open-interest cap overrides, as `[coin, cap]` pairs."""
  deployer: str
  """Address that deployed this perp dex."""
  deployerFeeScale: NotRequired[str]
  """Fee scale factor applied to the deployer's share of trading fees, as a decimal string."""
  feeRecipient: str | None
  """Address receiving the deployer's fee share, or `null` if unset."""
  fullName: str
  """Full display name of the perp dex."""
  lastDeployerFeeScaleChangeTime: NotRequired[str]
  """ISO 8601 timestamp of the last change to `deployerFeeScale`."""
  name: str
  """Short name of the perp dex."""
  oracleUpdater: str | None
  """Address authorized to push oracle price updates for this dex, or `null` if unset."""
  subDeployers: NotRequired[list[tuple[str, list[str]]]]
  """Sub-deployer permission grants, as `[action, addresses]` pairs."""


class PerpDexsAction(TypedDict):
  type: Literal['perpDexs']


adapter = pydantic.TypeAdapter(list[PerpDex | None])


class PerpDexs(InfoMixin):
  async def perp_dexs(self) -> list[PerpDex | None]:
    """Retrieve every perp dex on the venue, including builder-deployed (HIP-3) ones. The first entry is always `null`, representing the default first-party perp dex, which carries no deployer metadata.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: PerpDexsAction = {
      'type': 'perpDexs',
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
