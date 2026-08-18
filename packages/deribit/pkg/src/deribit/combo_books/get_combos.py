"""`public/get_combos` — `public/get_combos`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class ComboLeg(TypedDict):
  """One leg of a combo."""

  instrument_name: NotRequired[str]
  """Unique instrument identifier."""
  amount: NotRequired[int]
  """Size multiplier of this leg. A negative value indicates that trades on this leg run opposite to the combo trades they originate from."""


class Combo(TypedDict):
  """One combo book: a synthetic multi-leg instrument."""

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


validate_get_combos = validator[list[Combo]](list[Combo])


class GetCombos(RpcEndpoint):
  """`public/get_combos`."""

  async def get_combos(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any'],
    validate: bool | None = None,
  ) -> list[Combo]:
    """Retrieves information about active combos for the specified currency. Returns detailed information including leg structures and combo properties.

    For a list of combo IDs only, use `public/get_combo_ids`. For details about a specific combo, use `public/get_combo_details`.

    Args:
      currency: The currency symbol or `"any"` for all
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/combo-books/public-get_combos)
    """
    params: dict = {
      'currency': currency,
    }
    return await self.request(
      'public/get_combos',
      params=params,
      validator=validate_get_combos,
      validate=validate,
    )
