from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class PerpsAtOpenInterestCapAction(TypedDict):
  type: Literal['perpsAtOpenInterestCap']
  dex: NotRequired[str]


adapter = pydantic.TypeAdapter(list[str])


class PerpsAtOpenInterestCap(InfoMixin):
  async def perps_at_open_interest_cap(self, *, dex: str | None = None) -> list[str]:
    """List the coins on a perp dex that are currently at their open interest cap, and therefore only reduce-only for new orders.

    Args:
      dex: Perp dex name to scope the request to. Defaults to the empty string, which represents the first (default) perp dex.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: PerpsAtOpenInterestCapAction = {
      'type': 'perpsAtOpenInterestCap',
    }
    if dex is not None:
      params['dex'] = dex
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
