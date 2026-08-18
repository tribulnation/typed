from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FlexibleLoanRepaymentHistoryEntry(TypedDict):
  """One flexible loan repayment history entry."""

  loanCoin: NotRequired[str]
  """Loan coin."""
  repayAmount: NotRequired[str]
  """Amount repaid."""
  collateralCoin: NotRequired[str]
  """Collateral coin."""
  collateralReturn: NotRequired[str]
  """Collateral amount returned as a result of this repayment."""
  repayStatus: NotRequired[str]
  """Repayment status."""
  repayTime: NotRequired[int]
  """Millisecond epoch time of the repayment."""


class FlexibleLoanRepaymentHistoryPage(TypedDict):
  """One page of flexible loan repayment history."""

  rows: NotRequired[list[FlexibleLoanRepaymentHistoryEntry]]
  """Matching repayment history entries."""
  total: NotRequired[int]
  """Total number of matching history entries."""


class RepaymentHistory(RpcEndpoint):
  """Get Flexible Loan Repayment History. It can be used to check history before 2024-02-27 08:00."""

  async def repayment_history(
    self,
    *,
    loan_coin: str | None = None,
    collateral_coin: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> FlexibleLoanRepaymentHistoryPage:
    """Get Flexible Loan Repayment History. It can be used to check history before 2024-02-27 08:00.

    Args:
      loan_coin: Loan coin to filter by.
      collateral_coin: Collateral coin to filter by.
      start_time: Millisecond epoch lower bound. If both `startTime` and `endTime` are omitted, the most recent 90 days are returned.
      end_time: Millisecond epoch upper bound. Maximum interval between `startTime` and `endTime` is 180 days.
      current: Current page number, starting from 1.
      limit: Number of records per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-crypto-loan/api/rest-api/flexible-rate#get-flexible-loan-repayment-history)
    """
    params = {}
    if loan_coin is not None:
      params['loanCoin'] = loan_coin
    if collateral_coin is not None:
      params['collateralCoin'] = collateral_coin
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if limit is not None:
      params['limit'] = limit
    _Response = FlexibleLoanRepaymentHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v2/loan/flexible/repay/history',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def repayment_history_paged(
    self,
    *,
    loan_coin: str | None = None,
    collateral_coin: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[FlexibleLoanRepaymentHistoryPage]:
    """Yield successive pages of `repayment_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.repayment_history(
        loan_coin=loan_coin,
        collateral_coin=collateral_coin,
        start_time=start_time,
        end_time=end_time,
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
