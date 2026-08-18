"""`GET /api/v3/margin/borrowRate` — Get Borrow Interest Rate."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class MarginBorrowInterestRate(TypedDict):
  """Borrow interest rate for one currency."""

  currency: str
  """Currency code."""
  hourlyBorrowRate: str
  """Interest rate charged per hour of borrowing, as a decimal fraction."""
  annualizedBorrowRate: str
  """`hourlyBorrowRate` annualized, as a decimal fraction."""


class MarginBorrowInterestRates(TypedDict):
  """Borrow interest rates for a given VIP level."""

  vipLevel: int
  """VIP level these rates apply to."""
  items: list[MarginBorrowInterestRate]
  """Borrow interest rate per currency."""


_Type = MarginBorrowInterestRates
adapter = validator[_Type](_Type)  # type: ignore


class BorrowInterestRate(RpcEndpoint):
  """`Get Borrow Interest Rate` — mixed into `Debit`, the product exposing `margin.debit.borrow_interest_rate`."""

  async def borrow_interest_rate(
    self,
    *,
    currency: str | None = None,
    vip_level: int | None = None,
    validate: bool | None = None,
  ) -> MarginBorrowInterestRates:
    """Get the current margin-borrow interest rate for one or more currencies, at the caller's own VIP level.

    Args:
      currency: Comma-separated currency codes to filter by, e.g. `BTC,ETH`. Omitted returns every currency's rate.
      vip_level: VIP tier to price the rate at. Omitted uses the caller's own VIP level.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    if vip_level is not None:
      params['vipLevel'] = vip_level
    return await self.authed_request(
      'GET',
      '/api/v3/margin/borrowRate',
      params=params,
      validator=adapter,
      validate=validate,
    )
