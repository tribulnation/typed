"""`private/get_deposits` — `private/get_deposits`."""

from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Deposit(TypedDict):
  """One deposit transaction."""

  currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR']
  """The currency symbol."""
  address: str
  """Deribit's deposit address the funds were received at, in currency format."""
  amount: float
  """Amount of funds deposited, in `currency`."""
  state: Literal['pending', 'completed', 'rejected', 'replaced']
  """`pending`: detected on-chain, compliance not finished. `completed`: compliance finished successfully. `rejected`: failed compliance, needs manual handling. `replaced`: the transaction was replaced on-chain and should have a new transaction hash."""
  transaction_id: str | None
  """Transaction id in the currency's native format, `null` if not yet available."""
  source_address: NotRequired[str]
  """The sender's address, in currency format, when known."""
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
  """Status of the transaction clearance/compliance process, when applicable."""
  refund_transaction_id: NotRequired[str | None]
  """Transaction id of the refund, when `clearance_state` is a refund outcome; `null` otherwise or if not yet available."""


class DepositsPage(TypedDict):
  """One page of deposit history."""

  data: list[Deposit]
  """Deposits on this page, most recent first."""
  count: int
  """Total number of deposits available for `currency`, independent of `count`/`offset`."""


validate_get_deposits = validator[DepositsPage](DepositsPage)


class GetDeposits(RpcEndpoint):
  """`private/get_deposits`."""

  async def get_deposits(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    count: int | None = None,
    offset: int | None = None,
    validate: bool | None = None,
  ) -> DepositsPage:
    """Retrieve the latest user deposits. Returns a list of deposit transactions with their status, amounts, addresses, confirmations, and other relevant details.

    Args:
      currency: The currency symbol.
      count: Number of requested items, default `10`, maximum `1000`.
      offset: The offset for pagination, default `0`.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/wallet/private-get_deposits)
    """
    params: dict = {
      'currency': currency,
    }
    if count is not None:
      params['count'] = count
    if offset is not None:
      params['offset'] = offset
    return await self.authed_request(
      'private/get_deposits',
      params=params,
      validator=validate_get_deposits,
      validate=validate,
    )

  async def get_deposits_paged(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    count: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[DepositsPage]:
    """Yield successive pages of `get_deposits`.

    Advances `offset` by `(count if count is not None else 10)` and stops once it has
    covered the `count` items the response reports, or after `max_pages` pages when one
    is given.
    """
    offset = 0
    pages = 0
    while True:
      response = await self.get_deposits(
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
