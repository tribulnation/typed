from datetime import datetime
from typing_extensions import Any, Literal, NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Amount(TypedDict):
  """Gross amount of the movement, before withholding."""

  value: NotRequired[str]
  """Amount value."""
  currency: NotRequired[str]
  """Currency of the amount."""


class EarnMovementSource(TypedDict):
  """Wallet the funds were sourced from."""

  currency: NotRequired[str]
  """Currency of the source wallet."""
  walletId: NotRequired[str]
  """Identifier of the source wallet."""


class DataItem(TypedDict):
  movementId: NotRequired[str]
  """Unique identifier of the movement."""
  userId: NotRequired[str]
  """Identifier of the user the movement belongs to."""
  type: NotRequired[Literal['deposit', 'withdrawal', 'reward']]
  """Movement type."""
  status: NotRequired[str]
  """Processing status of the movement, as reported by the venue (e.g. `completed`)."""
  createdAt: NotRequired[datetime]
  """Date and time the movement was created."""
  updatedAt: NotRequired[datetime]
  """Date and time the movement was last updated."""
  walletId: NotRequired[str]
  """Identifier of the Earn wallet this movement belongs to."""
  lockId: NotRequired[str | None]
  """Identifier of the lock period associated with this movement, or null when the movement is not tied to one."""
  amount: NotRequired[Amount]
  withholdingAmount: NotRequired[dict[str, Any]]
  """Amount withheld (e.g. for tax purposes) from the movement."""
  netAmount: NotRequired[dict[str, Any]]
  """Amount net of withholding: `amount` minus `withholdingAmount`."""
  rate: NotRequired[dict[str, Any]]
  """Exchange rate applied when converting the movement amount, if applicable."""
  convertedAmount: NotRequired[dict[str, Any]]
  """Movement amount converted to `userCurrency` (or the account default), using `rate`."""
  source: NotRequired[EarnMovementSource | None]
  """Wallet the funds were sourced from (e.g. a reward's originating balance), or null when the movement has no originating wallet."""
  issuer: NotRequired[dict[str, Any]]
  """Origin of the movement: the client/integrator that created it (e.g. `{"integrator": "web"}`), or the internal service and reward id that generated it (e.g. `{"name": "earn-reward", "id": "..."}`)."""


class ListEarnWalletMovementsResponse(TypedDict):
  total: int
  """Total movements matching the query"""
  data: list[DataItem]
  """Earn movements returned"""


validate_response = validator(ListEarnWalletMovementsResponse)


class ListMovements(RpcEndpoint):
  async def list_movements(
    self,
    wallet_id: str,
    *,
    user_currency: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    sort_by: Literal['createdAt'] | None = None,
    sort_direction: Literal['ascending', 'descending'] | None = None,
    validate: bool | None = None,
  ) -> ListEarnWalletMovementsResponse:
    """Retrieve the wallet movement list.

    Movements can be paginated with `offset` and `limit`. For example, to fetch the third page with 20 records per page:

    ```text
    /v1/earn/wallets/{walletId}/movements?offset=40&limit=20
    ```

    Args:
      wallet_id: Wallet identifier
      user_currency: Currency to show convertedAmount
      offset: Specify the number of entries to be skipped (0 by default)
      limit: Specify the maximum number of entries to be returned (20 by default)
      sort_by: Sorting field
      sort_direction: Sorting direction
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/earn/GET/v1/earn/wallets/{walletId}/movements)
    """
    params = {}
    if user_currency is not None:
      params['userCurrency'] = user_currency
    if offset is not None:
      params['offset'] = offset
    if limit is not None:
      params['limit'] = limit
    if sort_by is not None:
      params['sortBy'] = sort_by
    if sort_direction is not None:
      params['sortDirection'] = sort_direction
    return await self.authed_request(
      'GET',
      f'/v1/earn/wallets/{wallet_id}/movements',
      params=params,
      validator=validate_response,
      validate=validate,
    )
