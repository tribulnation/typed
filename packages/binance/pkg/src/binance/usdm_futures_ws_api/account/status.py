from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class UsdMWsAccountAsset(TypedDict):
  """Per-asset balance and margin detail within a USD-M Futures account."""

  asset: str
  """Asset name."""
  walletBalance: str
  """Wallet balance."""
  unrealizedProfit: str
  """Unrealized profit."""
  marginBalance: str
  """Margin balance."""
  maintMargin: str
  """Maintenance margin requirement."""
  initialMargin: str
  """Total initial margin requirement."""
  positionInitialMargin: str
  """Initial margin required for positions."""
  openOrderInitialMargin: str
  """Initial margin required for open orders."""
  crossWalletBalance: str
  """Cross wallet balance."""
  crossUnPnl: str
  """Unrealized PnL for cross positions."""
  availableBalance: str
  """Available balance."""
  maxWithdrawAmount: str
  """Maximum transferable/withdrawable amount."""
  marginAvailable: bool
  """Whether the asset can be used as margin in multi-assets mode."""
  updateTime: int
  """Last update time, in milliseconds."""


class UsdMWsAccountStatusPosition(TypedDict):
  """Per-symbol position detail within account.status."""

  symbol: str
  """Trading symbol."""
  initialMargin: str
  """Initial margin requirement."""
  maintMargin: str
  """Maintenance margin requirement."""
  unrealizedProfit: str
  """Unrealized profit."""
  positionInitialMargin: str
  """Initial margin required for positions."""
  openOrderInitialMargin: str
  """Initial margin required for open orders."""
  leverage: str
  """Current initial leverage."""
  isolated: bool
  """Whether the position uses isolated margin mode."""
  entryPrice: str
  """Average entry price."""
  maxNotional: NotRequired[str]
  """Maximum available notional under current leverage."""
  bidNotional: NotRequired[str]
  """Bid notional (reserved, ignore)."""
  askNotional: NotRequired[str]
  """Ask notional (reserved, ignore)."""
  positionSide: Literal['BOTH', 'LONG', 'SHORT']
  """Position side."""
  positionAmt: str
  """Position quantity."""
  updateTime: int
  """Last update time, in milliseconds."""
  breakEvenPrice: NotRequired[str]
  """Break-even price."""


class UsdMWsAccountStatus(TypedDict):
  """Current USD-M Futures account information."""

  feeTier: int
  """Account commission tier."""
  canTrade: bool
  """Whether trading is enabled."""
  canDeposit: bool
  """Whether transfer-in is enabled."""
  canWithdraw: bool
  """Whether transfer-out is enabled."""
  updateTime: int
  """Reserved field, ignore."""
  multiAssetsMargin: bool
  """Whether multi-assets mode is enabled."""
  tradeGroupId: int
  """Trade group identifier."""
  totalInitialMargin: str
  """Total initial margin requirement. USDT only in single-asset mode; sum of USD value of all cross positions/open order initial margin in multi-assets mode."""
  totalMaintMargin: str
  """Total maintenance margin requirement. USDT only in single-asset mode; sum of USD value of all cross positions maintenance margin in multi-assets mode."""
  totalWalletBalance: str
  """Total wallet balance. USDT only in single-asset mode; USD-denominated in multi-assets mode."""
  totalUnrealizedProfit: str
  """Total unrealized profit. USDT only in single-asset mode; USD-denominated in multi-assets mode."""
  totalMarginBalance: str
  """Total margin balance. USDT only in single-asset mode; USD-denominated in multi-assets mode."""
  totalPositionInitialMargin: str
  """Initial margin required for positions. USDT only in single-asset mode; sum of USD value of all cross positions initial margin in multi-assets mode."""
  totalOpenOrderInitialMargin: str
  """Initial margin required for open orders. USDT only in single-asset mode; USD-denominated in multi-assets mode."""
  totalCrossWalletBalance: str
  """Cross wallet balance. USDT only in single-asset mode; USD-denominated in multi-assets mode."""
  totalCrossUnPnl: str
  """Unrealized PnL for cross positions. USDT only in single-asset mode; USD-denominated in multi-assets mode."""
  availableBalance: str
  """Available balance. USDT only in single-asset mode; USD-denominated in multi-assets mode."""
  maxWithdrawAmount: str
  """Maximum transferable/withdrawable amount. USDT only in single-asset mode; a maximum virtual USD amount in multi-assets mode."""
  assets: list[UsdMWsAccountAsset]
  """Asset-level account details."""
  positions: list[UsdMWsAccountStatusPosition]
  """Position details for symbols. One-way mode returns BOTH; hedge mode returns LONG/SHORT."""


class Status(WsRpcEndpoint):
  """Get current account information. A user in single-asset mode and one in multi-assets mode see different values for the USD-denominated total fields."""

  async def status(self, *, validate: bool | None = None) -> UsdMWsAccountStatus:
    """Get current account information. A user in single-asset mode and one in multi-assets mode see different values for the USD-denominated total fields.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-api/account#account-information)
    """
    _Response = UsdMWsAccountStatus
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'account.status', validator=_validator, validate=validate
    )
