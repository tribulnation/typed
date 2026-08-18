"""`public/get_combo_ids` — `public/get_combo_ids`."""

from typing_extensions import Literal
from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_get_combo_ids = validator[list[str]](list[str])


class GetComboIds(RpcEndpoint):
  """`public/get_combo_ids`."""

  async def get_combo_ids(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    state: Literal['active', 'inactive'] | None = None,
    validate: bool | None = None,
  ) -> list[str]:
    """Retrieves available combo IDs. This method can be used to get the list of all combos, or only the list of combos in the given state.

    Use `public/get_combo_details` to retrieve detailed information about a specific combo.

    Args:
      currency: The currency symbol
      state: Combo state, if not provided combos of all states are considered
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/combo-books/public-get_combo_ids)
    """
    params: dict = {
      'currency': currency,
    }
    if state is not None:
      params['state'] = state
    return await self.request(
      'public/get_combo_ids',
      params=params,
      validator=validate_get_combo_ids,
      validate=validate,
    )
