from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class BorrowLendUserStateAction(TypedDict):
  type: Literal['borrowLendUserState']
  user: str


class BorrowPosition(TypedDict):
  """The user's borrow position for this token."""

  basis: str
  """Borrowed principal basis, as a decimal string."""
  value: str
  """Current borrowed value including accrued interest, as a decimal string."""


class SupplyPosition(TypedDict):
  """The user's supply position for this token."""

  basis: str
  """Supplied principal basis, as a decimal string."""
  value: str
  """Current supplied value including accrued interest, as a decimal string."""


class BorrowLendTokenState(TypedDict):
  """The user's borrow and supply positions for a single token."""

  borrow: BorrowPosition
  supply: SupplyPosition


class BorrowLendUserState(TypedDict):
  """The user's borrow/lend account state."""

  tokenToState: list[tuple[int, BorrowLendTokenState]]
  """Per-token borrow/lend positions for the user, as `[tokenIndex, state]` pairs."""
  health: str
  """Account borrow/lend health status, e.g. `healthy` when collateral safely covers the debt. Hyperliquid's docs and every captured example show only `healthy`; the venue does not publish its full set of possible values."""
  healthFactor: str | None
  """Ratio measuring how far the account's borrow position is from liquidation, or `null` when the account has no open borrow position. Every captured example returned `null`."""


adapter = pydantic.TypeAdapter(BorrowLendUserState)


class BorrowLendUserStateEndpoint(InfoMixin):
  async def borrow_lend_user_state(self, *, user: str) -> BorrowLendUserState:
    """Query a user's borrow/lend account state, through Hyperliquid POST /info using request type `borrowLendUserState`. Includes per-token borrow and supply positions plus overall account health.

    Args:
      user: User address in 42-character hexadecimal format, e.g. 0x0000000000000000000000000000000000000000.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint#query-borrow-lend-user-state)
    """
    params: BorrowLendUserStateAction = {
      'type': 'borrowLendUserState',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
