from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class AllBorrowLendReserveStatesAction(TypedDict):
  type: Literal['allBorrowLendReserveStates']


class BorrowLendReserveState(TypedDict):
  """Borrow/lend reserve state for a single spot token."""

  borrowYearlyRate: str
  """Annualized interest rate charged to borrowers of this token, as a decimal fraction."""
  supplyYearlyRate: str
  """Annualized interest rate paid to suppliers of this token, as a decimal fraction."""
  balance: str
  """Total token balance held in the reserve, as a decimal string."""
  utilization: str
  """Fraction of supplied liquidity currently borrowed (totalBorrowed / totalSupplied), as a decimal fraction."""
  oraclePx: str
  """Oracle mark price of the token in USD, as a decimal string."""
  ltv: str
  """Maximum loan-to-value ratio accepted for this token as collateral, as a decimal fraction."""
  totalSupplied: str
  """Total amount of the token supplied to the reserve, as a decimal string."""
  totalBorrowed: str
  """Total amount of the token currently borrowed from the reserve, as a decimal string."""


adapter = pydantic.TypeAdapter(list[tuple[int, BorrowLendReserveState]])


class AllBorrowLendReserveStates(InfoMixin):
  async def all_borrow_lend_reserve_states(
    self,
  ) -> list[tuple[int, BorrowLendReserveState]]:
    """List the borrow/lend money-market reserve state for every spot token that has one.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: AllBorrowLendReserveStatesAction = {
      'type': 'allBorrowLendReserveStates',
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
