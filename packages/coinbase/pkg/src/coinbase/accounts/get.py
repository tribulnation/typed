from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Any, Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class AccountBalance(TypedDict):
  """The account's current balance."""

  amount: str
  """Balance amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class AccountCurrency(TypedDict):
  """The currency this account holds."""

  address_regex: NotRequired[str]
  """Regex an onchain deposit address for this currency must match."""
  asset_id: str
  """Coinbase's internal asset id."""
  code: str
  """Currency code, e.g. `BTC`."""
  color: str
  """Brand color, as a hex string."""
  exponent: int
  """Number of decimal places the currency's smallest unit represents."""
  name: str
  """Currency display name."""
  slug: str
  """URL-safe currency identifier."""
  sort_index: NotRequired[int]
  """Coinbase's display sort order for this currency."""
  type: str
  """Currency kind. Observed example value `crypto`; not documented as an exhaustive enumeration."""
  rewards: NotRequired[dict[str, Any] | None]
  """Rewards program metadata for this currency, if any. `null` when the currency has no active rewards program — verified live."""


class AccountV2(TypedDict):
  """A Coinbase App v2 account (wallet, vault, or fiat account)."""

  id: str
  """Account id."""
  name: str
  """User-assigned account name."""
  primary: bool
  """Whether this is the user's primary account for its currency. A user can only have one primary account, and it can only be `wallet`."""
  type: Literal['wallet', 'fiat', 'vault']
  """Account type."""
  currency: AccountCurrency
  balance: AccountBalance
  created_at: str
  """Account creation time, ISO 8601."""
  updated_at: str
  """Last account update time, ISO 8601."""
  resource: Literal['account']
  """Resource type tag."""
  resource_path: str
  """The account's own API path, e.g. `/v2/accounts/{id}`."""
  ready: NotRequired[bool]
  """Whether the account is fully provisioned and usable. Absent on some account types in observed responses."""


class ShowAccountResponse(TypedDict):
  """The whole v2 wire frame — not unwrapped by the core."""

  data: AccountV2


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /v2/accounts/{account_id}`."""

  async def __call__(self, account_id: str) -> ShowAccountResponse:
    """Get a single account by id. `account_id` also accepts a currency code (e.g. `BTC`), which resolves to that currency's account. Requires the `wallet:accounts:read` scope.

    Args:
      account_id: Account id, or a currency code (e.g. `BTC`) to look up that currency's account.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/track-apis/accounts)
    """
    return await self.authed_request(
      'GET', f'/v2/accounts/{account_id}', validator=validator(ShowAccountResponse)
    )
