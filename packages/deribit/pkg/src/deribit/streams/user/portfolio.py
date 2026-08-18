"""`user.portfolio.{currency}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class PortfolioUpdate(TypedDict):
  """Message schema for `user.portfolio.(currency)` subscription - contains the data payload"""

  currency: str
  """The selected currency"""
  equity: float
  """The account's current equity"""
  maintenance_margin: float
  """The maintenance margin. When cross collateral is enabled, this aggregated value is calculated by converting the sum of each cross collateral currency's value to the given currency, using each cross collateral currency's index."""
  initial_margin: float
  """The account's initial margin. When cross collateral is enabled, this aggregated value is calculated by converting the sum of each cross collateral currency's value to the given currency, using each cross collateral currency's index."""
  available_funds: float
  """The account's available funds. When cross collateral is enabled, this aggregated value is calculated by converting the sum of each cross collateral currency's value to the given currency, using each cross collateral currency's index."""
  available_withdrawal_funds: float
  """The account's available to withdrawal funds"""
  balance: float
  """The account's balance"""
  fee_balance: NotRequired[float]
  """The account's fee balance (it can be used to pay for fees)"""
  margin_balance: float
  """The account's margin balance. When cross collateral is enabled, this aggregated value is calculated by converting the sum of each cross collateral currency's value to the given currency, using each cross collateral currency's index."""
  session_upl: float
  """Session unrealized profit and loss"""
  session_rpl: float
  """Session realized profit and loss"""
  total_pl: float
  """Profit and loss"""
  options_pl: float
  """Options profit and Loss"""
  options_session_rpl: float
  """Options session realized profit and Loss"""
  options_session_upl: float
  """Options session unrealized profit and Loss"""
  options_delta: float
  """Options summary delta"""
  options_gamma: float
  """Options summary gamma"""
  options_theta: float
  """Options summary theta"""
  options_value: float
  """Options value"""
  options_vega: float
  """Options summary vega"""
  futures_pl: float
  """Futures profit and Loss"""
  futures_session_rpl: float
  """Futures session realized profit and Loss"""
  futures_session_upl: float
  """Futures session unrealized profit and Loss"""
  delta_total: NotRequired[float]
  """The sum of position deltas. 

**DeltaTotal = Net Transaction Delta of options + BTC Position of Futures**

The DeltaTotal uses the Net Transaction Delta (or price adjusted Delta) of the options, where Net Transaction Delta = Black Scholes Delta - Mark Price of Options.

This is because, from a risk perspective, we are interested in the change in Bitcoin price as the underlying changes.

You should actually treat your delta as **Equity + Delta Total** if you want to have less risk for your USD PnL.

⚠️ **During the 30 minute settlement period we decay your Delta.** See [Delta decay during settlement](https://support.deribit.com/hc/en-us/articles/25944751433757-Delta-decay-during-settlement) for more details."""
  delta_total_map: dict[str, Any]
  """Map of position sum's per index"""
  options_gamma_map: dict[str, Any]
  """Map of options' gammas per index"""
  options_theta_map: dict[str, Any]
  """Map of options' thetas per index"""
  options_vega_map: dict[str, Any]
  """Map of options' vegas per index"""
  projected_delta_total: float
  """The sum of position deltas without positions that will expire during closest expiration"""
  portfolio_margining_enabled: bool
  """When `true` portfolio margining is enabled for user"""
  cross_collateral_enabled: bool
  """When `true` cross collateral is enabled for user"""
  margin_model: str
  """Name of user's currently enabled margin model"""
  total_equity_usd: NotRequired[float]
  """Optional (only for users using cross margin). The account's total equity in all cross collateral currencies, expressed in USD"""
  total_initial_margin_usd: NotRequired[float]
  """Optional (only for users using cross margin). The account's total initial margin in all cross collateral currencies, expressed in USD"""
  total_maintenance_margin_usd: NotRequired[float]
  """Optional (only for users using cross margin). The account's total maintenance margin in all cross collateral currencies, expressed in USD"""
  total_margin_balance_usd: NotRequired[float]
  """Optional (only for users using cross margin). The account's total margin balance in all cross collateral currencies, expressed in USD"""
  total_delta_total_usd: NotRequired[float]
  """Optional (only for users using cross margin). The account's total delta total in all cross collateral currencies, expressed in USD"""
  projected_initial_margin: NotRequired[float]
  """Projected initial margin. When cross collateral is enabled, this aggregated value is calculated by converting the sum of each cross collateral currency's value to the given currency, using each cross collateral currency's index."""
  projected_maintenance_margin: float
  """Projected maintenance margin. When cross collateral is enabled, this aggregated value is calculated by converting the sum of each cross collateral currency's value to the given currency, using each cross collateral currency's index."""
  estimated_liquidation_ratio: NotRequired[float]
  """[DEPRECATED] Estimated Liquidation Ratio is returned only for users with `segregated_sm` margin model. Multiplying it by future position's market price returns its estimated liquidation price. Use estimated_liquidation_ratio_map instead."""
  estimated_liquidation_ratio_map: NotRequired[dict[str, Any]]
  """Map of Estimated Liquidation Ratio per index, it is returned only for users with `segregated_sm` margin model. Multiplying it by future position's market price returns its estimated liquidation price."""
  additional_reserve: NotRequired[float]
  """The account's balance reserved in other orders"""


validate_portfolio = validator[PortfolioUpdate](PortfolioUpdate)


class Portfolio(StreamEndpoint):
  """`user.portfolio.{currency}` subscription."""

  def portfolio(
    self,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[PortfolioUpdate, Any, Any]:
    """Real-time notifications for user portfolio information. This subscription provides comprehensive account and portfolio data for the specified currency, including balances, margins, profit and loss, and Greeks.

    Each notification includes:

    - **Account balances:** Current balance, equity, margin balance, available funds, and available withdrawal funds
    - **Margin information:** Initial margin, maintenance margin, and projected margins
    - **Profit and Loss:** Total P&L, session unrealized P&L (UPL), session realized P&L (RPL), and separate P&L for options and futures
    - **Options Greeks:** Delta, gamma, theta, vega, and options value, with per-index mappings
    - **Position data:** Delta total, projected delta total, and delta total map per index
    - **Account settings:** Portfolio margining status, cross collateral status, and margin model
    - **Cross collateral data:** Total equity, margins, and delta in USD (when cross collateral is enabled)
    - **Additional reserves:** Fee balance and additional reserve information

    When cross collateral is enabled, aggregated values are calculated by converting the sum of each cross collateral currency's value to the given currency, using each cross collateral currency's index.

    Subscribe to a specific currency (BTC, ETH, USDC, USDT, etc.) or use `any` to receive portfolio updates for all currencies.

    Args:
      currency: Currency code or `any` for all

    **Allowed values:** `BTC`, `ETH`, `USDC`, `USDT`, `EURR`, `any`
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/subscriptions/user-portfolio-currency)
    """
    channel = f'user.portfolio.{currency}'
    return self.authed_subscribe(
      channel, validator=validate_portfolio, validate=validate
    )
