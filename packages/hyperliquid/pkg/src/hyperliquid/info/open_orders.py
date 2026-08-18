from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class OpenOrder(TypedDict):
  """A single open order."""

  coin: str
  """Asset symbol the order is on."""
  limitPx: str
  """Limit price of the order."""
  oid: int
  """Order id."""
  side: Literal['A', 'B']
  """Order side: "A" (ask/sell) or "B" (bid/buy)."""
  sz: str
  """Remaining unfilled size of the order."""
  timestamp: int
  """Time the order was placed, in Unix epoch milliseconds."""


class OpenOrdersAction(TypedDict):
  type: Literal['openOrders']
  user: str
  dex: NotRequired[str]


adapter = pydantic.TypeAdapter(list[OpenOrder])


class OpenOrders(InfoMixin):
  async def open_orders(self, *, user: str, dex: str | None = None) -> list[OpenOrder]:
    """Retrieve a user's currently open orders through Hyperliquid POST /info using request type `openOrders`.

    Args:
      user: Onchain address in 42-character hexadecimal format, e.g. 0x0000000000000000000000000000000000000000.
      dex: Perp dex name. Defaults to the empty string, which represents the first perp dex. Spot open orders are only included with the first perp dex.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: OpenOrdersAction = {
      'type': 'openOrders',
      'user': user,
    }
    if dex is not None:
      params['dex'] = dex
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
