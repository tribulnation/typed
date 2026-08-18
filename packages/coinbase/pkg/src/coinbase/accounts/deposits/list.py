from dataclasses import dataclass
from datetime import datetime
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint
from coinbase.types import (
  Money,
  PaymentMethodReference,
  TransactionReference,
  V2pagination,
)


class Deposit(TypedDict):
  """A deposit of funds into a fiat account using a linked payment method. Each committed deposit also has an associated transaction."""

  id: str
  """Resource id."""
  status: Literal['created', 'completed', 'canceled']
  """Status of the deposit."""
  payment_method: PaymentMethodReference
  transaction: TransactionReference
  amount: Money
  subtotal: Money
  fee: Money
  created_at: datetime
  """When this deposit was created, RFC3339."""
  updated_at: datetime
  """When this deposit was last updated, RFC3339."""
  resource: Literal['deposit']
  """Resource type, always `deposit`."""
  resource_path: str
  """API path to fetch this deposit resource."""
  payout_at: NotRequired[datetime | None]
  """When a deposit that isn't executed instantly will pay out, RFC3339, or null when not applicable."""
  commited: bool
  """Whether this deposit has been committed. Verified live: the wire key is `commited` (single 't'), not `committed` as documented."""


class ListDepositsResponse(TypedDict):
  """A page of an account's deposits."""

  pagination: V2pagination
  data: list[Deposit]
  """The account's deposits on this page."""


@dataclass(frozen=True, kw_only=True)
class List(RpcEndpoint):
  """`GET /v2/accounts/{account_id}/deposits`."""

  async def list(
    self,
    account_id: str,
    *,
    limit: int | None = None,
    order: Literal['desc', 'asc'] | None = None,
    starting_after: str | None = None,
    ending_before: str | None = None,
  ) -> ListDepositsResponse:
    """List fiat deposits for an account.

    Args:
      account_id: The fiat account to list deposits for.
      limit: Number of results per call. Accepted values: 0-100.
      order: Result order.
      starting_after: Pagination cursor: the id of the resource that defines the caller's place in the list, exclusive, walking towards newer entries.
      ending_before: Pagination cursor: the id of the resource that defines the caller's place in the list, exclusive, walking towards older entries.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/transfer-apis/deposit-fiat)
    """
    params = {}
    if limit is not None:
      params['limit'] = limit
    if order is not None:
      params['order'] = order
    if starting_after is not None:
      params['starting_after'] = starting_after
    if ending_before is not None:
      params['ending_before'] = ending_before
    return await self.authed_request(
      'GET',
      f'/v2/accounts/{account_id}/deposits',
      params=params,
      validator=validator(ListDepositsResponse),
    )
