from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class VipLoanFixedRateSupplyOrder(TypedDict):
  """One fixed-rate supply order available in the market."""

  requestId: NotRequired[int]
  """Supply request ID."""
  requestNo: NotRequired[int]
  """Request number."""
  coin: NotRequired[str]
  """Coin."""
  interestRate: NotRequired[str]
  """Annual interest rate, as a decimal string."""
  duration: NotRequired[int]
  """Duration in days."""
  minimumAmount: NotRequired[str]
  """Minimum borrow amount."""
  availableAmount: NotRequired[str]
  """Maximum available borrow amount."""
  estimatedInterest: NotRequired[str]
  """Estimated interest for a full-amount borrow."""


class VipLoanFixedRateMarketPage(TypedDict):
  """One page of the VIP loan fixed-rate supply market."""

  total: NotRequired[int]
  """Total number of matching supply orders."""
  rows: NotRequired[list[VipLoanFixedRateSupplyOrder]]
  """Matching supply orders on this page."""


class FixedRateMarket(RpcEndpoint):
  """Query the VIP loan fixed rate market. Returns a paginated list of fixed-rate supply orders available to borrow against."""

  async def fixed_rate_market(
    self,
    *,
    loan_coin: str,
    duration: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> VipLoanFixedRateMarketPage:
    """Query the VIP loan fixed rate market. Returns a paginated list of fixed-rate supply orders available to borrow against.

    Args:
      loan_coin: Loan coin to query the fixed-rate market for.
      duration: Duration in days to filter supply orders by.
      current: Page number, default 1, minimum 1.
      size: Page size, default 10, range [1, 100].

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#query-viploan-fixed-rate-market)
    """
    params: dict = {
      'loanCoin': loan_coin,
    }
    if duration is not None:
      params['duration'] = duration
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = VipLoanFixedRateMarketPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/loan/vip/fixed/market',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def fixed_rate_market_paged(
    self,
    *,
    loan_coin: str,
    duration: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[VipLoanFixedRateMarketPage]:
    """Yield successive pages of `fixed_rate_market`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.fixed_rate_market(
        loan_coin=loan_coin,
        duration=duration,
        size=size,
        current=current,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or size is None or pages * size >= total:
        break
      current += 1
