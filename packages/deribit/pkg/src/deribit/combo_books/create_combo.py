"""`private/create_combo` — `private/create_combo`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class ComboLeg(TypedDict):
  """One leg of a combo."""

  instrument_name: NotRequired[str]
  """Unique instrument identifier."""
  amount: NotRequired[int]
  """Size multiplier of this leg. A negative value indicates that trades on this leg run opposite to the combo trades they originate from."""


class ComboTrade(TypedDict):
  """One trade/leg used to build the combo."""

  instrument_name: str
  """Unique instrument identifier."""
  amount: float
  """It represents the requested order size. For perpetual and inverse futures the amount is in USD units. For options and linear futures it is the underlying base currency coin."""
  direction: Literal['buy', 'sell']
  """Direction: `buy`, or `sell`."""


class Combo(TypedDict):
  """The combo book that was created, or the pre-existing one matching the given trades."""

  id: NotRequired[str]
  """Unique combo identifier."""
  instrument_id: NotRequired[int]
  """Instrument id."""
  state: NotRequired[Literal['active', 'inactive']]
  """Combo state: `"active"`, `"inactive"`."""
  state_timestamp: NotRequired[int]
  """When the combo last changed state (milliseconds since the Unix epoch)."""
  creation_timestamp: NotRequired[int]
  """When the combo was created (milliseconds since the Unix epoch)."""
  legs: NotRequired[list[ComboLeg]]
  """The combo's leg structure."""


validate_create_combo = validator[Combo](Combo)


class CreateCombo(RpcEndpoint):
  """`private/create_combo`."""

  async def create_combo(
    self,
    *,
    trades: list[ComboTrade],
    validate: bool | None = None,
  ) -> Combo:
    """Verifies and creates a combo book or returns an existing combo matching the given trades. Combos allow trading on multiple instruments (futures and options) simultaneously as a single strategy.

    If a combo matching the provided trades already exists, this method returns the existing combo. Otherwise, it creates a new combo book with the specified leg structure.

    Args:
      trades: List of trades used to create a combo
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/combo-books/private-create_combo)
    """
    params: dict = {
      'trades': trades,
    }
    return await self.authed_request(
      'private/create_combo',
      params=params,
      validator=validate_create_combo,
      validate=validate,
    )
