"""`private/cancel_withdrawal` — `private/cancel_withdrawal`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Withdrawal(TypedDict):
  """The cancelled withdrawal."""

  address: str
  """Destination address, in currency format."""
  amount: float
  """Amount of funds withdrawn, in `currency`."""
  confirmed_timestamp: NotRequired[int | None]
  """Time the withdrawal was confirmed (milliseconds since the Unix epoch), `null` when not yet confirmed."""
  created_timestamp: NotRequired[int]
  """Time the withdrawal was created (milliseconds since the Unix epoch)."""
  currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR']
  """The currency symbol."""
  fee: NotRequired[float]
  """Fee charged for the withdrawal, in `currency`."""
  id: NotRequired[int]
  """Withdrawal id in the Deribit system."""
  priority: NotRequired[float]
  """Id of the priority level applied to this withdrawal."""
  state: Literal[
    'unconfirmed', 'confirmed', 'cancelled', 'completed', 'interrupted', 'rejected'
  ]
  """Withdrawal state. Expected to read `cancelled` on a successful call."""
  transaction_id: str | None
  """Transaction id in the currency's native format, `null` if not yet available."""
  updated_timestamp: int
  """Time this withdrawal record was last updated (milliseconds since the Unix epoch)."""
  nonce: NotRequired[str]
  """Optional idempotency nonce, when one was provided in the originating request."""


validate_cancel_withdrawal = validator[Withdrawal](Withdrawal)


class CancelWithdrawal(RpcEndpoint):
  """`private/cancel_withdrawal`."""

  async def cancel_withdrawal(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    id: int,
    validate: bool | None = None,
  ) -> Withdrawal:
    """Cancels a pending withdrawal request. Once a withdrawal has been processed it can no longer be cancelled.

    Args:
      currency: The currency symbol.
      id: The withdrawal id.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/wallet/private-cancel_withdrawal)
    """
    params: dict = {
      'currency': currency,
      'id': id,
    }
    return await self.authed_request(
      'private/cancel_withdrawal',
      params=params,
      validator=validate_cancel_withdrawal,
      validate=validate,
    )
