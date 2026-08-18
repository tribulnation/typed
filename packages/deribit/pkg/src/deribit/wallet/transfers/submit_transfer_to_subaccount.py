"""`private/submit_transfer_to_subaccount` — `private/submit_transfer_to_subaccount`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Transfer(TypedDict):
  """One internal transfer."""

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
  """Transfer state. Documented as an open set (`prepared`, `confirmed`, `cancelled`, `waiting_for_admin`, `insufficient_funds`, `withdrawal_limit`, or otherwise a rejection-reason string) -- see this endpoint's notes; left bare rather than a guessed closed `enum`."""
  direction: NotRequired[Literal['payment', 'income']]
  """Whether this transfer was sent (`payment`) or received (`income`)."""
  updated_timestamp: int
  """Time this transfer record was last updated (milliseconds since the Unix epoch)."""
  nonce: NotRequired[str]
  """Optional idempotency nonce, when one was provided in the originating request."""
  source: NotRequired[int]
  """Id of the (sub)account that initiated the transfer (observed live; not in the venue's own documented `transfer_item` schema -- see this endpoint's notes)."""
  note: NotRequired[str]
  """Free-text note attached to the transfer (observed live as an empty string in every capture; not in the venue's own documented `transfer_item` schema -- see this endpoint's notes)."""


validate_submit_transfer_to_subaccount = validator[Transfer](Transfer)


class SubmitTransferToSubaccount(RpcEndpoint):
  """`private/submit_transfer_to_subaccount`."""

  async def submit_transfer_to_subaccount(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    amount: float,
    destination: int,
    validate: bool | None = None,
  ) -> Transfer:
    """Transfer funds from the main account to a subaccount.

    Args:
      currency: The currency symbol.
      amount: Amount of funds to be transferred.
      destination: Id of the destination subaccount. Can be found in `My Account >> Subaccounts`.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/wallet/private-submit_transfer_to_subaccount)
    """
    params: dict = {
      'currency': currency,
      'amount': amount,
      'destination': destination,
    }
    return await self.authed_request(
      'private/submit_transfer_to_subaccount',
      params=params,
      validator=validate_submit_transfer_to_subaccount,
      validate=validate,
    )
