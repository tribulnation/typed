"""`private/set_clearance_originator` — `private/set_clearance_originator`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Deposit(TypedDict):
  """The deposit whose clearance-process originator was just set."""

  currency: str
  """The currency symbol."""
  user_id: int
  """Unique user identifier."""
  address: str
  """Deribit's deposit address the funds were received at, in currency format."""
  amount: float
  """Amount of funds deposited, in `currency`."""
  state: Literal['pending', 'completed', 'rejected', 'replaced']
  """`pending`: detected on-chain, compliance not finished. `completed`: compliance finished successfully. `rejected`: failed compliance, needs manual handling. `replaced`: the transaction was replaced on-chain and should have a new transaction hash."""
  transaction_id: str
  """Transaction id in the currency's native format."""
  source_address: NotRequired[str]
  """The sender's address, in currency format."""
  received_timestamp: int
  """Time the deposit was received (milliseconds since the Unix epoch)."""
  updated_timestamp: int
  """Time this deposit record was last updated (milliseconds since the Unix epoch)."""
  note: NotRequired[str]
  """Free-text note attached to the deposit, when any."""
  clearance_state: NotRequired[
    Literal[
      'in_progress',
      'pending_admin_decision',
      'pending_user_input',
      'success',
      'failed',
      'cancelled',
      'refund_initiated',
      'refunded',
    ]
  ]
  """Status of the transaction clearance/compliance process."""


validate_set_clearance_originator = validator[Deposit](Deposit)


class SetClearanceOriginator(RpcEndpoint):
  """`private/set_clearance_originator`."""

  async def set_clearance_originator(
    self,
    *,
    deposit_id: str,
    originator: str,
    validate: bool | None = None,
  ) -> Deposit:
    """Sets originator of the deposit.

    Args:
      deposit_id: Id of the deposit, as a JSON string containing: `currency`, `user_id`, `address`, `tx_hash`.
      originator: Information about the originator of the deposit, as a JSON string containing: `is_personal`, `company_name`, `first_name`, `last_name`, `address`.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/wallet/private-set_clearance_originator)
    """
    params: dict = {
      'deposit_id': deposit_id,
      'originator': originator,
    }
    return await self.authed_request(
      'private/set_clearance_originator',
      params=params,
      validator=validate_set_clearance_originator,
      validate=validate,
    )
