"""dYdX indexer parent-subaccount funding payment pagination.

Hand-written: `get_funding_payments_for_parent_subaccount`'s pagination has no declared
`spec/endpoints/.../endpoint.json` `pagination` block yet (a `page` walk that trusts the
response's own `pageSize`/`totalResults`/`offset` envelope fields where present, and
falls back to "stop on the first empty page" otherwise). Kept in its own file, separate
from the codegen-owned `get_funding_payments_for_parent_subaccount.py`, so re-running
codegen doesn't overwrite it -- mirrors `chain/modules/tx/get_txs_event_paged.py`'s own
precedent.
"""

from dataclasses import dataclass
from datetime import datetime

from typed_core import PaginatedResponse

from typed_dydx.indexer.schemas import FundingPayment

from .get_funding_payments_for_parent_subaccount import (
  GetFundingPaymentsForParentSubaccount,
)


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
