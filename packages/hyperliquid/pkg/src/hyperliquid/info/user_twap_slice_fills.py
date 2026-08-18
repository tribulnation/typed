from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class TwapFill(TypedDict):
  """A single fill produced by one slice of a TWAP order."""

  coin: str
  """Traded asset: a perp coin name, a HIP-3 perp prefixed with its dex name (e.g. `xyz:XYZ100`), or a spot pair (`PURR/USDC`, or `@{index}` for any other spot pair)."""
  px: str
  """Fill price, as a decimal string."""
  sz: str
  """Fill size, as a decimal string."""
  side: Literal['A', 'B']
  """Fill side: `B` (bid, the buyer's side) or `A` (ask, the seller's side)."""
  time: int
  """Fill time, in milliseconds since epoch."""
  startPosition: str
  """Signed position size immediately before the fill, as a decimal string."""
  dir: Literal['Open Long', 'Buy', 'Sell']
  """Human-readable fill direction/effect label."""
  closedPnl: str
  """Realized PnL closed by this fill, as a decimal string."""
  hash: str
  """L1 transaction hash of the fill. Always the zero hash (`0x00...00`) for TWAP slice fills."""
  oid: int
  """Id of the order that produced this fill."""
  crossed: bool
  """Whether this fill was the taker side of the trade (crossed the book)."""
  fee: str
  """Total fee charged for the fill, inclusive of `builderFee`, as a decimal string."""
  feeToken: str
  """Token the fee is denominated in, e.g. `USDC` or `HYPE`."""
  builderFee: NotRequired[str]
  """Builder fee portion of `fee`, as a decimal string. Present only when nonzero."""
  tid: int
  """Trade id. Not a unique key: every `Spot Dust Conversion` fill carries the sentinel value `0`."""


class UserTwapSliceFillsAction(TypedDict):
  type: Literal['userTwapSliceFills']
  user: str


class UserTwapSliceFill(TypedDict):
  """A single TWAP slice fill and the TWAP order it belongs to."""

  fill: TwapFill
  twapId: int
  """Id of the TWAP order this slice fill belongs to."""


adapter = pydantic.TypeAdapter(list[UserTwapSliceFill])


class UserTwapSliceFills(InfoMixin):
  async def user_twap_slice_fills(self, *, user: str) -> list[UserTwapSliceFill]:
    """Retrieve a user's most recent TWAP slice fills. Returns at most 2000 of the most recent TWAP slice fills.

    Args:
      user: Account address to query, in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000. Must be the actual account address of the master or sub-account being queried -- an agent wallet's address returns an empty result.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: UserTwapSliceFillsAction = {
      'type': 'userTwapSliceFills',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
