"""dYdX indexer get funding payments types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typed_core import PaginatedResponse
from .. import timestamp as ts
from typing_extensions import Literal, TypedDict
from .core import IndexerMixin, response_parser

class FundingPayment(TypedDict):
  """FundingPayment payload."""
  createdAt: datetime
  createdAtHeight: str
  perpetualId: str
  ticker: str
  oraclePrice: Decimal
  size: Decimal
  side: Literal['LONG', 'SHORT']
  rate: Decimal
  payment: Decimal
  subaccountNumber: str
  fundingIndex: Decimal

class FundingPaymentsResponse(TypedDict):
  """Funding payments response payload."""
  fundingPayments: list[FundingPayment]

parse_response = response_parser(FundingPaymentsResponse)

@dataclass
class GetFundingPayments(IndexerMixin):
  """Endpoint mixin for funding_payments."""
  async def get_funding_payments(
    self,
    address: str,
    *,
    subaccount: int,
    ticker: str | None = None,
    after_or_at: datetime | None = None,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None
  ) -> FundingPaymentsResponse:
    """Fetch funding payments for a subaccount.
  
    Args:
      address: Wallet address that owns the subaccount.
      subaccount: Subaccount number.
      ticker: Market ticker filter.
      after_or_at: Earliest timestamp to include.
      limit: Maximum number of funding payments to return.
      page: Page number for paginated results.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-funding-payments)
    """
    params: dict[str, object] = {
      'address': address,
      'subaccountNumber': subaccount,
    }
    if ticker is not None:
      params['ticker'] = ticker
    if after_or_at is not None:
      params['afterOrAt'] = ts.dump(after_or_at)
    if limit is not None:
      params['limit'] = limit
    if page is not None:
      params['page'] = page
    r = await self.request('GET', '/v4/fundingPayments', params=params)
    return parse_response(r, validate=self.validate(validate))

@dataclass
class GetFundingPaymentsPaged(GetFundingPayments):
  """Endpoint mixin for funding_payments_paged."""
  def get_funding_payments_paged(
    self,
    address: str,
    *,
    subaccount: int,
    ticker: str | None = None,
    after_or_at: datetime | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[FundingPayment, int]:
    """Page through funding payments for a subaccount.
  
    Args:
      address: The wallet address that owns the account.
      subaccount: The identifier for the specific subaccount within the wallet address.
      ticker: The market ticker (e.g. `'BTC-USD'`).
      after_or_at: If given, fetches funding payments starting from the given timestamp.
      limit: The max. number of funding payments to retrieve.
      validate: Override the client response validation default for this call.
  
    Returns:
      A paginated response. Each request advances by page number until the endpoint returns no items.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-funding-payments)
    """
    async def next(page: int) -> tuple[list[FundingPayment], int | None]:
      """Next.
    
      Args:
        page: Page number to request.
      """
      response = await self.get_funding_payments(
        address,
        subaccount=subaccount,
        ticker=ticker,
        after_or_at=after_or_at,
        limit=limit,
        page=page,
        validate=validate,
      )
      funding_payments = response['fundingPayments']
      next_page = page + 1 if funding_payments else None
      return funding_payments, next_page

    return PaginatedResponse(1, next)
