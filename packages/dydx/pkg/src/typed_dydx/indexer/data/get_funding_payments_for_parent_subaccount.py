"""dYdX indexer get funding payments for parent subaccount types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typed_core import PaginatedResponse
from .. import timestamp as ts
from typing_extensions import Literal, NotRequired, TypedDict
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
  pageSize: NotRequired[int]
  """Number of results requested per page."""
  totalResults: NotRequired[int]
  """Total number of results matching the request."""
  offset: NotRequired[int]
  """Zero-based result offset for this page."""


parse_response = response_parser(FundingPaymentsResponse)


@dataclass
class GetFundingPaymentsForParentSubaccount(IndexerMixin):
  """Endpoint mixin for funding_payments_for_parent_subaccount."""

  async def get_funding_payments_for_parent_subaccount(
    self,
    address: str,
    *,
    parent_subaccount: int,
    limit: int | None = None,
    after_or_at: datetime | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> FundingPaymentsResponse:
    """Get funding payments for parent subaccount.

    Args:
      address: Wallet address that owns the account.
      parent_subaccount: Parent subaccount number.
      limit: Maximum number of results to return.
      after_or_at: Only include payments created at or after this timestamp.
      page: Page number for paginated results.
      validate: Override the client response validation default for this call.

    Returns:
      The validated indexer response payload.

    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-funding-payments-for-parent-subaccount)
    """
    params: dict[str, object] = {
      'address': address,
      'parentSubaccountNumber': parent_subaccount,
    }
    if limit is not None:
      params['limit'] = limit
    if after_or_at is not None:
      params['afterOrAt'] = ts.dump(after_or_at)
    if page is not None:
      params['page'] = page
    r = await self.request('GET', '/v4/fundingPayments/parentSubaccount', params=params)
    return parse_response(r, validate=self.validate(validate))


@dataclass
class GetFundingPaymentsForParentSubaccountPaged(GetFundingPaymentsForParentSubaccount):
  """Endpoint mixin for parent-subaccount funding payment pagination."""

  def get_funding_payments_for_parent_subaccount_paged(
    self,
    address: str,
    *,
    parent_subaccount: int,
    limit: int | None = None,
    after_or_at: datetime | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[FundingPayment, int]:
    """Page through funding payments for a parent subaccount.

    Args:
      address: Wallet address that owns the account.
      parent_subaccount: Parent subaccount number.
      limit: Maximum number of results to request per page.
      after_or_at: Only include payments created at or after this timestamp.
      validate: Override the client response validation default for this call.

    Returns:
      A paginated response. Pagination metadata determines completion when present;
      otherwise requests continue until the endpoint returns no items.

    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-funding-payments-for-parent-subaccount)
    """

    async def next(page: int) -> tuple[list[FundingPayment], int | None]:
      """Fetch the requested page and determine its successor.

      Args:
        page: Page number to request.

      Returns:
        The page items and next page number, if any.
      """
      response = await self.get_funding_payments_for_parent_subaccount(
        address,
        parent_subaccount=parent_subaccount,
        limit=limit,
        after_or_at=after_or_at,
        page=page,
        validate=validate,
      )
      funding_payments = response['fundingPayments']
      page_size = response.get('pageSize')
      total_results = response.get('totalResults')
      offset = response.get('offset')
      if page_size is not None and total_results is not None and offset is not None:
        has_next = offset + page_size < total_results
      else:
        has_next = bool(funding_payments)
      return funding_payments, page + 1 if has_next else None

    return PaginatedResponse(1, next)
