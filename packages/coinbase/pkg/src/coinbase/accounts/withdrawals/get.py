from dataclasses import dataclass
from datetime import datetime
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint
from coinbase.types import Money, PaymentMethodReference, TransactionReference


class Withdrawal(TypedDict):
  """A withdrawal of funds from a fiat account to a linked payment method. Each committed withdrawal also has an associated transaction."""

  id: str
  """Resource id."""
  status: Literal['created', 'completed', 'canceled']
  """Status of the withdrawal."""
  payment_method: PaymentMethodReference
  transaction: TransactionReference
  amount: Money
  subtotal: Money
  fee: Money
  created_at: datetime
  """When this withdrawal was created, RFC3339."""
  updated_at: datetime
  """When this withdrawal was last updated, RFC3339."""
  resource: Literal['withdrawal']
  """Resource type, always `withdrawal`."""
  resource_path: str
  """API path to fetch this withdrawal resource."""
  payout_at: NotRequired[datetime | None]
  """When a withdrawal that isn't executed instantly will pay out, RFC3339, or null when not applicable."""
  commited: bool
  """Whether this withdrawal has been committed. Verified live: the wire key is `commited` (single 't'), not `committed` as documented."""


class GetWithdrawalResponse(TypedDict):
  """Wrapper around a single withdrawal."""

  data: Withdrawal


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /v2/accounts/{account_id}/withdrawals/{withdrawal_id}`."""

  async def get(self, account_id: str, withdrawal_id: str) -> GetWithdrawalResponse:
    """Get a single withdrawal.

    Args:
      account_id: The fiat account the withdrawal belongs to.
      withdrawal_id: The withdrawal to fetch.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/transfer-apis/withdraw-fiat)
    """
    return await self.authed_request(
      'GET',
      f'/v2/accounts/{account_id}/withdrawals/{withdrawal_id}',
      validator=validator(GetWithdrawalResponse),
    )
