"""`private/get_transfers` — `private/get_transfers`."""

from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
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


class TransfersPage(TypedDict):
  """One page of transfer history."""

  data: list[Transfer]
  """Transfers on this page, most recent first."""
  count: int
  """Total number of transfers available for `currency`, independent of `count`/`offset`."""


validate_get_transfers = validator[TransfersPage](TransfersPage)


class GetTransfers(RpcEndpoint):
  """`private/get_transfers`."""

  async def get_transfers(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    count: int | None = None,
    offset: int | None = None,
    validate: bool | None = None,
  ) -> TransfersPage:
    """Retrieve the user's transfers list. Returns a list of internal transfers between accounts, subaccounts, or to other users, including their status, amounts, and other relevant details.

    Args:
      currency: The currency symbol.
      count: Number of requested items, default `10`, maximum `1000`.
      offset: The offset for pagination, default `0`.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/wallet/private-get_transfers)
    """
    params: dict = {
      'currency': currency,
    }
    if count is not None:
      params['count'] = count
    if offset is not None:
      params['offset'] = offset
    return await self.authed_request(
      'private/get_transfers',
      params=params,
      validator=validate_get_transfers,
      validate=validate,
    )

  async def get_transfers_paged(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    count: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[TransfersPage]:
    """Yield successive pages of `get_transfers`.

    Advances `offset` by `(count if count is not None else 10)` and stops once it has
    covered the `count` items the response reports, or after `max_pages` pages when one
    is given.
    """
    offset = 0
    pages = 0
    while True:
      response = await self.get_transfers(
        currency=currency, count=count, offset=offset, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('count') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or count is None or pages * count >= total:
        break
      offset += count if count is not None else 10
