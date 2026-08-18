from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FlexibleLoanOngoingOrder(TypedDict):
  """One currently ongoing flexible loan order."""

  loanCoin: NotRequired[str]
  """Loan coin."""
  totalDebt: NotRequired[str]
  """Outstanding debt, principal plus accrued interest."""
  collateralCoin: NotRequired[str]
  """Collateral coin."""
  collateralAmount: NotRequired[str]
  """Current collateral amount pledged."""
  currentLTV: NotRequired[str]
  """Current LTV."""


class FlexibleLoanOngoingOrdersPage(TypedDict):
  """One page of currently ongoing flexible loan orders."""

  rows: NotRequired[list[FlexibleLoanOngoingOrder]]
  """Matching ongoing orders."""
  total: NotRequired[int]
  """Total number of matching ongoing orders."""


class OngoingOrders(RpcEndpoint):
  """Get Flexible Loan Ongoing Orders."""

  async def ongoing_orders(
    self,
    *,
    loan_coin: str | None = None,
    collateral_coin: str | None = None,
    current: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> FlexibleLoanOngoingOrdersPage:
    """Get Flexible Loan Ongoing Orders.

    Args:
      loan_coin: Loan coin to filter by.
      collateral_coin: Collateral coin to filter by.
      current: Current page number, starting from 1.
      limit: Number of records per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-crypto-loan/api/rest-api/flexible-rate#get-flexible-loan-ongoing-orders)
    """
    params = {}
    if loan_coin is not None:
      params['loanCoin'] = loan_coin
    if collateral_coin is not None:
      params['collateralCoin'] = collateral_coin
    if current is not None:
      params['current'] = current
    if limit is not None:
      params['limit'] = limit
    _Response = FlexibleLoanOngoingOrdersPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v2/loan/flexible/ongoing/orders',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def ongoing_orders_paged(
    self,
    *,
    loan_coin: str | None = None,
    collateral_coin: str | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[FlexibleLoanOngoingOrdersPage]:
    """Yield successive pages of `ongoing_orders`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.ongoing_orders(
        loan_coin=loan_coin,
        collateral_coin=collateral_coin,
        limit=limit,
        current=current,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or limit is None or pages * limit >= total:
        break
      current += 1
