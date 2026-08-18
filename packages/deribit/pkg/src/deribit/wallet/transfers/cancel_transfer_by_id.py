"""`private/cancel_transfer_by_id` — `private/cancel_transfer_by_id`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Transfer(TypedDict):
  """The cancelled transfer."""

  id: int
  """Id of the transfer."""
  created_timestamp: int
  """Time the transfer was created (milliseconds since the Unix epoch)."""
  type: Literal['user', 'subaccount']
  """`user`: sent to another user. `subaccount`: sent to a subaccount."""
  currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR']
  """The currency symbol."""
  amount: float
  """Amount of funds transferred, in `currency`."""
  other_side: str
  """For a subaccount transfer, the subaccount's name; for a transfer to another account, the destination address; for a transfer from another account, the sender's username."""
  state: str
  """Transfer state. Documented as an open set (`prepared`, `confirmed`, `cancelled`, `waiting_for_admin`, `insufficient_funds`, `withdrawal_limit`, or otherwise a rejection-reason string) -- see this endpoint's notes; left bare rather than a guessed closed `enum`. Expected to read `cancelled` on a successful call."""
  direction: NotRequired[Literal['payment', 'income']]
  """Whether this transfer was sent (`payment`) or received (`income`)."""
  updated_timestamp: int
  """Time this transfer record was last updated (milliseconds since the Unix epoch)."""
  nonce: NotRequired[str]
  """Optional idempotency nonce, when one was provided in the originating request."""
  source: NotRequired[int]
  """Id of the (sub)account that initiated the transfer (observed live on sibling transfer endpoints; not in the venue's own documented `transfer_item` schema -- see this endpoint's notes)."""
  note: NotRequired[str]
  """Free-text note attached to the transfer (observed live on sibling transfer endpoints as an empty string; not in the venue's own documented `transfer_item` schema -- see this endpoint's notes)."""


validate_cancel_transfer_by_id = validator[Transfer](Transfer)


class CancelTransferById(RpcEndpoint):
  """`private/cancel_transfer_by_id`."""

  async def cancel_transfer_by_id(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    id: int,
    validate: bool | None = None,
  ) -> Transfer:
    """Cancel a pending transfer by its id. Once a transfer has been processed it can no longer be cancelled.

    Args:
      currency: The currency symbol.
      id: Id of the transfer to cancel.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/wallet/private-cancel_transfer_by_id)
    """
    params: dict = {
      'currency': currency,
      'id': id,
    }
    return await self.authed_request(
      'private/cancel_transfer_by_id',
      params=params,
      validator=validate_cancel_transfer_by_id,
      validate=validate,
    )
