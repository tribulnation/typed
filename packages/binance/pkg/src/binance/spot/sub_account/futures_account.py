from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FuturesAccountAsset(TypedDict):
  """One asset's margin/balance detail within a futures account."""

  asset: NotRequired[str]
  """Asset symbol."""
  initialMargin: NotRequired[str]
  """Initial margin required across open positions and orders."""
  maintenanceMargin: NotRequired[str]
  """Maintenance margin required across open positions."""
  marginBalance: NotRequired[str]
  """Margin balance (wallet balance plus unrealized profit)."""
  maxWithdrawAmount: NotRequired[str]
  """Maximum amount currently withdrawable."""
  openOrderInitialMargin: NotRequired[str]
  """Initial margin required by open orders."""
  positionInitialMargin: NotRequired[str]
  """Initial margin required by open positions."""
  unrealizedProfit: NotRequired[str]
  """Unrealized profit/loss."""
  walletBalance: NotRequired[str]
  """Wallet balance."""


class SubAccountFuturesAccount(TypedDict):
  """Futures account detail."""

  email: NotRequired[str]
  """Sub-account email."""
  assets: NotRequired[list[FuturesAccountAsset]]
  """Per-asset margin/balance detail."""
  canDeposit: NotRequired[bool]
  """Whether the account can deposit."""
  canTrade: NotRequired[bool]
  """Whether the account can trade."""
  canWithdraw: NotRequired[bool]
  """Whether the account can withdraw."""
  feeTier: NotRequired[int]
  """Account fee tier."""
  maxWithdrawAmount: NotRequired[str]
  """Maximum amount currently withdrawable."""
  totalInitialMargin: NotRequired[str]
  """Total initial margin required across positions and orders."""
  totalMaintenanceMargin: NotRequired[str]
  """Total maintenance margin required across positions."""
  totalMarginBalance: NotRequired[str]
  """Total margin balance across all assets."""
  totalOpenOrderInitialMargin: NotRequired[str]
  """Total initial margin required by open orders."""
  totalPositionInitialMargin: NotRequired[str]
  """Total initial margin required by open positions."""
  totalUnrealizedProfit: NotRequired[str]
  """Total unrealized profit/loss across all assets."""
  totalWalletBalance: NotRequired[str]
  """Total wallet balance across all assets."""
  updateTime: NotRequired[int]
  """Time the account snapshot was taken."""


class FuturesAccount(RpcEndpoint):
  """Get detail on a sub-account's USD-M futures account, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    validate: bool | None = None,
  ) -> SubAccountFuturesAccount:
    """Get detail on a sub-account's USD-M futures account, for the master account.

    Args:
      email: Sub-account email.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#get-detail-on-sub-accounts-futures-account)
    """
    params: dict = {
      'email': email,
    }
    _Response = SubAccountFuturesAccount
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/futures/account',
      params=params,
      validator=_validator,
      validate=validate,
    )
