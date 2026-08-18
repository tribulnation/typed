from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Any, AsyncIterator, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class V3balance(TypedDict):
  """Balance available to trade or withdraw."""

  value: str
  """Balance amount, as a decimal string."""
  currency: str
  """Currency code of `value`."""


class V3account(TypedDict):
  """An Advanced Trade brokerage account."""

  uuid: str
  """Account id."""
  name: str
  """Account display name."""
  currency: str
  """Currency code this account holds."""
  available_balance: V3balance
  default: bool
  """Whether this is the default account for its currency."""
  active: bool
  """Whether the account is active."""
  created_at: str
  """Account creation time, ISO 8601."""
  updated_at: str
  """Last account update time, ISO 8601."""
  deleted_at: NotRequired[str | None]
  """Account deletion time, ISO 8601, or null if not deleted."""
  type: str
  """Account type. Observed example value `FIAT`; the fetched docs page did not enumerate the closed set of values, so this is left untyped rather than guessed."""
  ready: bool
  """Whether the account is fully provisioned and usable."""
  hold: dict[str, Any]
  """Balance currently held (e.g. by open orders), same shape as `available_balance`."""
  retail_portfolio_id: str
  """The portfolio this account belongs to."""
  platform: str
  """Platform the account is scoped to. Observed example value `ACCOUNT_PLATFORM_CONSUMER`; the fetched docs page did not enumerate the closed set of values, so this is left untyped rather than guessed."""


class V3accountsPage(TypedDict):
  accounts: list[V3account]
  """The account list for this page."""
  has_next: bool
  """Whether a next page exists."""
  cursor: str
  """Cursor to pass as `cursor` to fetch the next page."""
  size: int
  """Number of accounts in this page."""


@dataclass(frozen=True, kw_only=True)
class List(RpcEndpoint):
  """`GET /api/v3/brokerage/accounts`."""

  async def list(
    self,
    *,
    limit: int | None = None,
    cursor: str | None = None,
    retail_portfolio_id: str | None = None,
  ) -> V3accountsPage:
    """List the CDP API Key's Advanced Trade v3 brokerage accounts.

    Args:
      limit: The number of accounts to display per page.
      cursor: For paginated responses, returns all accounts that come after this value.
      retail_portfolio_id: Deprecated parameter retained for legacy keys only.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/accounts/list-accounts)
    """
    params = {}
    if limit is not None:
      params['limit'] = limit
    if cursor is not None:
      params['cursor'] = cursor
    if retail_portfolio_id is not None:
      params['retail_portfolio_id'] = retail_portfolio_id
    return await self.authed_request(
      'GET',
      '/api/v3/brokerage/accounts',
      params=params,
      validator=validator(V3accountsPage),
    )

  async def list_paged(
    self,
    *,
    limit: int | None = None,
    retail_portfolio_id: str | None = None,
    max_pages: int | None = None,
  ) -> AsyncIterator[V3accountsPage]:
    """Yield successive pages of `list`.

    Passes each page's token back as `cursor` and stops when a response carries no
    `cursor`, or after `max_pages` pages when one is given.
    """
    cursor: str | None = None
    pages = 0
    while True:
      response = await self.list(
        limit=limit, retail_portfolio_id=retail_portfolio_id, cursor=cursor
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      cursor = response.get('cursor') if response is not None else None
      if not cursor:
        break
