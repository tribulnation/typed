from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class FrontendOpenOrder(TypedDict):
  """A single open order, with the extra fields the Hyperliquid frontend displays. Upstream docs show no `tif`, `cloid`, or `children` fields on this shape, unlike the equivalent order object returned by `orderStatus`/`historicalOrders`; no live example with a non-empty order list was captured to confirm this against a real response."""

  coin: str
  """Asset symbol the order is on."""
  isPositionTpsl: bool
  """Whether this order is a take-profit/stop-loss order tied to the whole position, rather than a standalone order."""
  isTrigger: bool
  """Whether this is a trigger order (activates once `triggerPx` is reached) rather than a resting limit/market order."""
  limitPx: str
  """Limit price of the order."""
  oid: int
  """Order id."""
  orderType: str
  """Display name of the order type, e.g. "Limit" or "Market". Upstream docs show only these two example values without publishing the full set of possible display names (e.g. stop/take-profit variants), so this is left unenumerated."""
  origSz: str
  """Original size the order was placed with."""
  reduceOnly: bool
  """Whether the order is restricted to only reducing an existing position."""
  side: Literal['A', 'B']
  """Order side: "A" (ask/sell) or "B" (bid/buy)."""
  sz: str
  """Remaining unfilled size of the order."""
  timestamp: int
  """Time the order was placed, in Unix epoch milliseconds."""
  triggerCondition: str
  """Human-readable trigger condition for a trigger order, e.g. "N/A" when the order has no trigger."""
  triggerPx: str
  """Trigger price for a trigger order; "0.0" when the order has no trigger."""


class FrontendOpenOrdersAction(TypedDict):
  type: Literal['frontendOpenOrders']
  user: str
  dex: NotRequired[str]


adapter = pydantic.TypeAdapter(list[FrontendOpenOrder])


class FrontendOpenOrders(InfoMixin):
  async def frontend_open_orders(
    self,
    *,
    user: str,
    dex: str | None = None,
  ) -> list[FrontendOpenOrder]:
    """Retrieve a user's currently open orders, including the extra display fields (order type, trigger condition, reduce-only, position TP/SL) the Hyperliquid frontend shows, through Hyperliquid POST /info using request type `frontendOpenOrders`.

    Args:
      user: Onchain address in 42-character hexadecimal format, e.g. 0x0000000000000000000000000000000000000000.
      dex: Perp dex name. Defaults to the empty string, which represents the first perp dex. Spot open orders are only included with the first perp dex.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: FrontendOpenOrdersAction = {
      'type': 'frontendOpenOrders',
      'user': user,
    }
    if dex is not None:
      params['dex'] = dex
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
