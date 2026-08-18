"""`private/get_account_summary` — `private/get_account_summary`."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class ChangeMarginModelApiLimit(TypedDict):
  """Rate limit on `private/change_margin_model` calls. Not in the venue's own documented schema for this field, observed live."""

  timeframe: int
  """Rolling window (milliseconds) the limit applies over."""
  rate: int
  """Maximum number of `change_margin_model` calls allowed in the window."""


class TradingProductDetail(TypedDict):
  product: str
  """Trading product name, e.g. `"perpetual"`, `"futures"`, `"options"`, `"future_combos"`, `"option_combos"`, `"spots"`. Not declared `enum`: this field is not documented on this operation at all (an undocumented addition beyond the venue's published schema), so only the observed values are known, not a closed set."""
  enabled: bool
  """Whether this trading product is enabled for the account."""
  overwriteable: NotRequired[bool]
  """Whether this setting can be overridden."""
  requires_consent: NotRequired[bool]
  """Whether enabling this product requires user consent."""


class AccountSummary(TypedDict):
  currency: str
  """The currency this summary is for."""
  balance: float
  """The account's balance."""
  equity: float
  """The account's current equity."""
  margin_balance: NotRequired[float]
  """The account's margin balance. When cross collateral is enabled, this aggregated value converts the sum of each cross collateral currency's value using each currency's index."""
  available_funds: float
  """The account's available funds (cross-collateral-aggregated when enabled)."""
  available_withdrawal_funds: float
  """The account's available-to-withdraw funds."""
  initial_margin: float
  """The account's initial margin (cross-collateral-aggregated when enabled)."""
  maintenance_margin: float
  """The maintenance margin (cross-collateral-aggregated when enabled)."""
  projected_initial_margin: NotRequired[float]
  """Projected initial margin."""
  projected_maintenance_margin: NotRequired[float]
  """Projected maintenance margin."""
  total_pl: float
  """Total profit and loss."""
  session_rpl: float
  """Session realized profit and loss."""
  session_upl: float
  """Session unrealized profit and loss."""
  futures_pl: NotRequired[float]
  """Futures profit and loss."""
  futures_session_rpl: NotRequired[float]
  """Futures session realized profit and loss."""
  futures_session_upl: NotRequired[float]
  """Futures session unrealized profit and loss."""
  options_pl: NotRequired[float]
  """Options profit and loss."""
  options_session_rpl: NotRequired[float]
  """Options session realized profit and loss."""
  options_session_upl: NotRequired[float]
  """Options session unrealized profit and loss."""
  options_delta: NotRequired[float]
  """Options summary delta."""
  options_gamma: NotRequired[float]
  """Options summary gamma."""
  options_theta: NotRequired[float]
  """Options summary theta."""
  options_vega: NotRequired[float]
  """Options summary vega."""
  options_value: NotRequired[float]
  """Options value."""
  options_gamma_map: NotRequired[dict[str, float]]
  """Map of options' gammas per index."""
  options_theta_map: NotRequired[dict[str, float]]
  """Map of options' thetas per index."""
  options_vega_map: NotRequired[dict[str, float]]
  """Map of options' vegas per index."""
  delta_total: NotRequired[float]
  """The sum of position deltas (net transaction delta of options plus futures BTC position)."""
  delta_total_map: NotRequired[dict[str, float]]
  """Map of total deltas per index. Not in the venue's own documented schema for this field, observed live."""
  projected_delta_total: NotRequired[float]
  """The sum of position deltas excluding positions expiring in the closest expiration."""
  spot_reserve: NotRequired[float]
  """The account's balance reserved in active spot orders."""
  additional_reserve: NotRequired[float]
  """The account's balance reserved in other orders."""
  fee_balance: NotRequired[float]
  """The account's fee balance (usable to pay fees)."""
  fee_group: NotRequired[str]
  """Fee group indicating the level of fee discounts applied to the account; only present when `extended` is `true` and the account is assigned to a fee group."""
  deposit_address: NotRequired[str]
  """The deposit address for the account, if available."""
  estimated_liquidation_ratio: NotRequired[float]
  """Estimated liquidation ratio, returned only for users without portfolio margining enabled; multiplying it by a future position's market price gives its estimated liquidation price."""
  estimated_liquidation_ratio_map: NotRequired[dict[str, float]]
  """Map of estimated liquidation ratios per index. Not in the venue's own documented schema for this field, observed live."""
  portfolio_margining_enabled: NotRequired[bool]
  """Whether portfolio margining is enabled for the user."""
  cross_collateral_enabled: NotRequired[bool]
  """Whether cross collateral is enabled for the user."""
  margin_model: NotRequired[str]
  """Name of the user's currently enabled margin model."""
  total_equity_usd: NotRequired[float]
  """Optional (cross-margin users only). The account's total equity across all cross collateral currencies, in USD."""
  total_initial_margin_usd: NotRequired[float]
  """Optional (cross-margin users only). The account's total initial margin across all cross collateral currencies, in USD."""
  total_maintenance_margin_usd: NotRequired[float]
  """Optional (cross-margin users only). The account's total maintenance margin across all cross collateral currencies, in USD."""
  total_margin_balance_usd: NotRequired[float]
  """Optional (cross-margin users only). The account's total margin balance across all cross collateral currencies, in USD."""
  total_delta_total_usd: NotRequired[float]
  """Optional (cross-margin users only). The account's total delta total across all cross collateral currencies, in USD."""
  limits: NotRequired[dict[str, Any]]
  """Rate-limit usage/limits for the account, per the Rate Limits reference (`non_matching_engine`, `matching_engine`, `limits_per_currency`)."""
  locked_balance: NotRequired[float]
  """The account's locked balance. Not in the venue's own documented schema for this field, observed live."""
  close_out_margin: NotRequired[float]
  """The account's close-out margin. Not in the venue's own documented schema for this field, observed live."""
  projected_close_out_margin: NotRequired[float]
  """Projected close-out margin. Not in the venue's own documented schema for this field, observed live."""
  id: NotRequired[int]
  """Account id. Available when `extended` is `true` (`get_account_summary`); always present in `get_account_summaries`."""
  username: NotRequired[str]
  """Account name given by the user."""
  email: NotRequired[str]
  """User email."""
  type: NotRequired[Literal['main', 'subaccount']]
  """Account type."""
  system_name: NotRequired[str]
  """System-generated user nickname."""
  security_keys_enabled: NotRequired[bool]
  """Whether Security Keys authentication is enabled."""
  mmp_enabled: NotRequired[bool]
  """Whether Market Maker Protection is enabled."""
  login_enabled: NotRequired[bool]
  """Whether the account is loginable using email and password (subaccounts only)."""
  interuser_transfers_enabled: NotRequired[bool]
  """Whether inter-user transfers are enabled for the user."""
  referrer_id: NotRequired[str | None]
  """Identifier of the referrer whose affiliation link this account registered through, when any -- the suffix of the affiliation link path after `/reg-`."""
  creation_timestamp: NotRequired[int]
  """Time the account was created (milliseconds since the Unix epoch)."""
  receive_notifications: NotRequired[bool]
  """Whether the account receives notifications."""
  is_direct_access_allowed: NotRequired[bool]
  """Whether Direct Access trading is enabled for the account."""
  self_trading_reject_mode: NotRequired[str]
  """Self-trading rejection behavior: `reject_taker` or `cancel_maker`."""
  self_trading_extended_to_subaccounts: NotRequired[bool]
  """Whether self-trading rejection behavior extends to trades between subaccounts."""
  trading_products_details: NotRequired[list[TradingProductDetail]]
  """Per-product trading enablement details."""
  affiliate_promotion_fee: NotRequired[float]
  """Affiliate promotion fee, if greater than 0."""
  has_non_block_chain_equity: NotRequired[bool]
  """Whether the user has non-blockchain equity excluded from proof-of-reserve calculations."""
  fees: NotRequired[dict[str, Any]]
  """Fee structure for all currency pairs and instrument types related to the currency. Keys are index names (e.g. `"btc_usd"`); values are objects keyed by instrument type (`option`, `future`, `perpetual`), each carrying a `default` fee entry (`{type, taker, maker}`) and an optional `block_trade` fee. Available when `extended` is `true` and the user has any discounts."""
  user_origin: NotRequired[str]
  """Origin of the account, e.g. `"deribit"`. Not in the venue's own documented schema for this field, observed live."""
  disable_kyc_verification: NotRequired[bool]
  """Whether KYC verification is disabled for this account. Not in the venue's own documented schema for this field, observed live."""
  mandatory_tfa: NotRequired[bool]
  """Whether two-factor authentication is mandatory for this account. Not in the venue's own documented schema for this field, observed live."""
  block_rfq_self_match_prevention: NotRequired[bool]
  """Whether Block RFQ self-match prevention is enabled. Not in the venue's own documented schema for this field, observed live."""
  change_margin_model_api_limit: NotRequired[ChangeMarginModelApiLimit]


validate_get_account_summary = validator[AccountSummary](AccountSummary)


class GetAccountSummary(RpcEndpoint):
  """`private/get_account_summary`."""

  async def get_account_summary(
    self,
    *,
    currency: Literal[
      'BTC',
      'ETH',
      'STETH',
      'ETHW',
      'USDC',
      'USDT',
      'EURR',
      'SOL',
      'XRP',
      'USYC',
      'PAXG',
      'BNB',
      'USDE',
    ],
    subaccount_id: int | None = None,
    extended: bool | None = None,
    validate: bool | None = None,
  ) -> AccountSummary:
    """Retrieves the account summary for a specific currency: balance, equity, available funds, initial/maintenance margin, and related information. To retrieve the summary for a specific subaccount, use `subaccount_id`. When `extended` is `true`, additional account details (id, username, email, type, ...) are included.

    Args:
      currency: The currency symbol.
      subaccount_id: The user id for the subaccount.
      extended: Include additional account-identity fields.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-get_account_summary)
    """
    params: dict = {
      'currency': currency,
    }
    if subaccount_id is not None:
      params['subaccount_id'] = subaccount_id
    if extended is not None:
      params['extended'] = extended
    return await self.authed_request(
      'private/get_account_summary',
      params=params,
      validator=validate_get_account_summary,
      validate=validate,
    )
