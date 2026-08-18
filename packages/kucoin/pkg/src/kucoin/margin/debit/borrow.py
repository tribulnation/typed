"""`POST /api/v3/margin/borrow` — Borrow."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BorrowRequest(TypedDict):
  currency: str
  """Currency to borrow, e.g. `BTC`, `ETH`, `USDT`."""
  size: float
  """Amount to borrow."""
  timeInForce: Literal['IOC', 'FOK']
  """Order execution rule."""
  symbol: NotRequired[str]
  """Trading pair, e.g. `BTC-USDT`. Mandatory when `isIsolated` is true; not required for cross margin."""
  isIsolated: NotRequired[bool]
  """Whether this is an isolated-margin borrow (`true`) or cross-margin (`false`)."""
  isHf: NotRequired[bool]
  """Whether this is a high-frequency borrow."""


class BorrowResult(TypedDict):
  orderNo: str
  """Unique id assigned to the new borrow order."""
  actualSize: str
  """Actual amount borrowed."""


_Type = BorrowResult
adapter = validator[_Type](_Type)  # type: ignore


class Borrow(RpcEndpoint):
  """`Borrow` — mixed into `Debit`, the product exposing `margin.debit.borrow`."""

  async def borrow(
    self,
    borrow_request: BorrowRequest,
    *,
    validate: bool | None = None,
  ) -> BorrowResult:
    """Initiate an application for cross or isolated margin borrowing.

    Args:
      borrow_request: Borrow parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/margin/borrow',
      json=borrow_request,
      validator=adapter,
      validate=validate,
    )
