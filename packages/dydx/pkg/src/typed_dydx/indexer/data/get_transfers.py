"""dYdX indexer get transfers types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typed_core import PaginatedResponse
from .. import timestamp as ts
from typing_extensions import Literal, NotRequired, TypedDict
from .core import IndexerMixin, response_parser

class Account(TypedDict):
  """Account payload."""
  address: str
  subaccountNumber: NotRequired[int|None]

class Transfer(TypedDict):
  """Transfer payload."""
  id: str
  sender: Account
  recipient: Account
  size: Decimal
  createdAt: datetime
  createdAtHeight: str
  symbol: str
  type: Literal['TRANSFER_IN', 'TRANSFER_OUT', 'DEPOSIT', 'WITHDRAWAL']
  transactionHash: str

class TransfersResponse(TypedDict):
  """Transfers response payload."""
  transfers: list[Transfer]

parse_response = response_parser(TransfersResponse)

@dataclass
class GetTransfers(IndexerMixin):
  """Endpoint mixin for transfers."""
  async def get_transfers(
    self,
    address: str,
    *,
    subaccount: int,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None
  ) -> TransfersResponse:
    """Fetch transfers for a subaccount.
  
    Args:
      address: Wallet address that owns the subaccount.
      subaccount: Subaccount number.
      created_before_or_at_height: Latest block height to include.
      created_before_or_at: Latest timestamp to include.
      limit: Maximum number of transfers to return.
      page: Page number for paginated results.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-transfers)
    """
    params: dict[str, object] = {
      'address': address,
      'subaccountNumber': subaccount,
    }
    if created_before_or_at_height is not None:
      params['createdBeforeOrAtHeight'] = created_before_or_at_height
    if created_before_or_at is not None:
      params['createdBeforeOrAt'] = ts.dump(created_before_or_at)
    if limit is not None:
      params['limit'] = limit
    if page is not None:
      params['page'] = page
    r = await self.request('GET', '/v4/transfers', params=params)
    return parse_response(r, validate=self.validate(validate))

@dataclass
class GetTransfersPaged(GetTransfers):
  """Endpoint mixin for transfers_paged."""
  def get_transfers_paged(
    self,
    address: str,
    *,
    subaccount: int,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[Transfer, int]:
    """Page through transfers for a subaccount.
  
    Args:
      address: The wallet address that owns the account.
      subaccount: The identifier for the specific subaccount within the wallet address.
      created_before_or_at_height: If given, fetches transfers up to and including the given block height.
      created_before_or_at: If given, fetches transfers up to and including the given timestamp.
      limit: The max. number of transfers to retrieve (default: 1000, max: 1000).
      validate: Override the client response validation default for this call.
  
    Returns:
      A paginated response. Each request advances by page number until the endpoint returns no items.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-transfers)
    """
    async def next(page: int) -> tuple[list[Transfer], int | None]:
      """Next.
    
      Args:
        page: Page number to request.
      """
      response = await self.get_transfers(
        address,
        subaccount=subaccount,
        created_before_or_at_height=created_before_or_at_height,
        created_before_or_at=created_before_or_at,
        limit=limit,
        page=page,
        validate=validate,
      )
      transfers = response['transfers']
      next_page = page + 1 if transfers else None
      return transfers, next_page

    return PaginatedResponse(1, next)
