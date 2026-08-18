from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class PerpDexStatus(TypedDict):
  """A perp dex's aggregate collateral status."""

  totalNetDeposit: str
  """Total USDC net-deposited into the perp dex, as a decimal string."""


class PerpDexStatusAction(TypedDict):
  type: Literal['perpDexStatus']
  dex: str


adapter = pydantic.TypeAdapter(PerpDexStatus)


class PerpDexStatusEndpoint(InfoMixin):
  async def perp_dex_status(self, *, dex: str) -> PerpDexStatus:
    """Retrieve a perp dex's total net deposit -- the aggregate USDC collateral currently backing the dex.

    Args:
      dex: Perp dex name to look up. The empty string represents the first (default) perp dex.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: PerpDexStatusAction = {
      'type': 'perpDexStatus',
      'dex': dex,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
