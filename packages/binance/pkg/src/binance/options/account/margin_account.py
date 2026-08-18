from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class MarginAsset(TypedDict):
  """Per-asset margin balances."""

  asset: NotRequired[str]
  """Asset."""
  marginBalance: NotRequired[str]
  """Margin balance."""
  equity: NotRequired[str]
  """Equity."""
  available: NotRequired[str]
  """Available balance."""
  initialMargin: NotRequired[str]
  """Initial margin."""
  maintMargin: NotRequired[str]
  """Maintenance margin."""
  unrealizedPNL: NotRequired[str]
  """Unrealized profit/loss."""
  adjustedEquity: NotRequired[str]
  """Adjusted equity."""


class MarginGreek(TypedDict):
  """Per-underlying aggregate Greeks."""

  underlying: NotRequired[str]
  """Underlying asset."""
  delta: NotRequired[str]
  """Aggregate delta for this underlying."""
  gamma: NotRequired[str]
  """Aggregate gamma for this underlying."""
  theta: NotRequired[str]
  """Aggregate theta for this underlying."""
  vega: NotRequired[str]
  """Aggregate vega for this underlying."""


class MarginAccount(TypedDict):
  """Option margin account information: equity/available/margin plus Greeks per underlying."""

  asset: NotRequired[list[MarginAsset]]
  """Per-asset margin balances."""
  greek: NotRequired[list[MarginGreek]]
  """Per-underlying aggregate Greeks."""
  time: NotRequired[Timestamp]
  """Time this snapshot was produced."""
  canTrade: NotRequired[bool]
  """Whether the account can trade."""
  canDeposit: NotRequired[bool]
  """Whether the account can deposit."""
  canWithdraw: NotRequired[bool]
  """Whether the account can withdraw."""
  reduceOnly: NotRequired[bool]
  """Whether the account is in reduce-only mode."""
  tradeGroupId: NotRequired[int]
  """Trade group ID."""


class MarginAccountEndpoint(RpcEndpoint):
  """Get current option margin account information. This is the account-info endpoint for Options — there is no separate `account` endpoint."""

  async def margin_account(self, *, validate: bool | None = None) -> MarginAccount:
    """Get current option margin account information. This is the account-info endpoint for Options — there is no separate `account` endpoint.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/account#option-margin-account-information)
    """
    _Response = MarginAccount
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/eapi/v1/marginAccount', validator=_validator, validate=validate
    )
