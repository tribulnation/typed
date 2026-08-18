"""`private/get_withdrawals` — `private/get_withdrawals`."""

from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Withdrawal(TypedDict):
  """One withdrawal request."""

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
  """Withdrawal state."""
  transaction_id: str | None
  """Transaction id in the currency's native format, `null` if not yet available."""
  updated_timestamp: int
  """Time this withdrawal record was last updated (milliseconds since the Unix epoch)."""
  nonce: NotRequired[str]
  """Optional idempotency nonce, when one was provided in the originating request."""


class WithdrawalsPage(TypedDict):
  """One page of withdrawal history."""

  data: list[Withdrawal]
  """Withdrawals on this page, most recent first."""
  count: int
  """Total number of withdrawals available for `currency`, independent of `count`/`offset`."""


validate_get_withdrawals = validator[WithdrawalsPage](WithdrawalsPage)


class GetWithdrawals(RpcEndpoint):
  """`private/get_withdrawals`."""

  async def get_withdrawals(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    count: int | None = None,
    offset: int | None = None,
    validate: bool | None = None,
  ) -> WithdrawalsPage:
    """Retrieve the latest user withdrawals. Returns a list of withdrawal requests with their status, amounts, addresses, and other relevant details.

    Args:
      currency: The currency symbol.
      count: Number of requested items, default `10`, maximum `1000`.
      offset: The offset for pagination, default `0`.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/wallet/private-get_withdrawals)
    """
    params: dict = {
      'currency': currency,
    }
    if count is not None:
      params['count'] = count
    if offset is not None:
      params['offset'] = offset
    return await self.authed_request(
      'private/get_withdrawals',
      params=params,
      validator=validate_get_withdrawals,
      validate=validate,
    )

  async def get_withdrawals_paged(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    count: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[WithdrawalsPage]:
    """Yield successive pages of `get_withdrawals`.

    Advances `offset` by `(count if count is not None else 10)` and stops once it has
    covered the `count` items the response reports, or after `max_pages` pages when one
    is given.
    """
    offset = 0
    pages = 0
    while True:
      response = await self.get_withdrawals(
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
