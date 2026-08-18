"""dYdX indexer get transfers between types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
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
class GetTransfersBetween(IndexerMixin):
  """Endpoint mixin for transfers_between."""
  async def get_transfers_between(
    self,
    source_address: str,
    *,
    source_subaccount: str,
    recipient_address: str,
    recipient_subaccount: str,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    validate: bool | None = None
  ) -> TransfersResponse:
    """Get transfers between.
  
    Args:
      source_address: Sender wallet address.
      source_subaccount: Sender subaccount number.
      recipient_address: Recipient wallet address.
      recipient_subaccount: Recipient subaccount number.
      created_before_or_at_height: Restrict results to entries created at or before a specific block height.
      created_before_or_at: Restrict results to entries created at or before a specific timestamp.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-transfers-between)
    """
    params: dict[str, object] = {
      'sourceAddress': source_address,
      'sourceSubaccountNumber': source_subaccount,
      'recipientAddress': recipient_address,
      'recipientSubaccountNumber': recipient_subaccount,
    }
    if created_before_or_at_height is not None:
      params['createdBeforeOrAtHeight'] = created_before_or_at_height
    if created_before_or_at is not None:
      params['createdBeforeOrAt'] = ts.dump(created_before_or_at)
    r = await self.request('GET', '/v4/transfers/between', params=params)
    return parse_response(r, validate=self.validate(validate))
