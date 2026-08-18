from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class SpotBalance(TypedDict):
  """A single spot token balance."""

  coin: str
  """Spot asset symbol, e.g. "USDC" or "HYPE"."""
  token: int
  """Spot token index."""
  hold: str
  """Amount of the balance currently held (locked) by open orders."""
  total: str
  """Total balance of the token, including any amount on hold."""
  entryNtl: str
  """Notional value of the balance at acquisition."""


class SpotClearinghouseStateAction(TypedDict):
  type: Literal['spotClearinghouseState']
  user: str


class SpotClearinghouseState(TypedDict):
  balances: list[SpotBalance]
  """The user's spot token balances."""
  tokenToAvailableAfterMaintenance: NotRequired[list[tuple[int, str]]]
  """Per-token amount still available after maintenance-margin requirements are met. Not documented upstream; observed only on responses carrying non-empty `balances`. Each row is `[token index, available amount]`."""


adapter = pydantic.TypeAdapter(SpotClearinghouseState)


class SpotClearinghouseStateEndpoint(InfoMixin):
  async def spot_clearinghouse_state(self, *, user: str) -> SpotClearinghouseState:
    """Retrieve a user's spot token balances through Hyperliquid POST /info using request type `spotClearinghouseState`.

    Args:
      user: Onchain address in 42-character hexadecimal format, e.g. 0x0000000000000000000000000000000000000000.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: SpotClearinghouseStateAction = {
      'type': 'spotClearinghouseState',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
