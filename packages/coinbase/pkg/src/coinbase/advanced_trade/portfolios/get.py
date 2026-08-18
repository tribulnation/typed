from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class AmountAvailableToTradeEquity(TypedDict):
  """Balance available to trade, in shares."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountAvailableToTradeFiat(TypedDict):
  """Balance available to trade, in fiat."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountCurrentPrice(TypedDict):
  """Current contract price."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountEquityPositionsItemAverageEntryPrice(TypedDict):
  """Average price paid across all fills."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountEquityPositionsItemCostBasis(TypedDict):
  """Total cost basis of this position."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountFuturesUnrealizedPnl(TypedDict):
  """Unrealized PnL on futures positions."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountImNotionalRawCurrency(TypedDict):
  """Value in the position's raw (quote) currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountImNotionalUserNativeCurrency(TypedDict):
  """Value in the user's native currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountItemUnrealizedPnl(TypedDict):
  """Unrealized profit/loss on this position."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountLiquidationPriceRawCurrency(TypedDict):
  """Value in the position's raw (quote) currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountLiquidationPriceUserNativeCurrency(TypedDict):
  """Value in the user's native currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountMarkPriceRawCurrency(TypedDict):
  """Value in the position's raw (quote) currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountMarkPriceUserNativeCurrency(TypedDict):
  """Value in the user's native currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountMmNotionalRawCurrency(TypedDict):
  """Value in the position's raw (quote) currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountMmNotionalUserNativeCurrency(TypedDict):
  """Value in the user's native currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountNotionalValue(TypedDict):
  """Total notional value of this position."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountPerpUnrealizedPnl(TypedDict):
  """Unrealized PnL on perpetuals positions."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountPositionNotionalRawCurrency(TypedDict):
  """Value in the position's raw (quote) currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountPositionNotionalUserNativeCurrency(TypedDict):
  """Value in the user's native currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountPredictionMarketsAverageEntryPrice(TypedDict):
  """Average entry price across contracts owned."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountPredictionMarketsCostBasis(TypedDict):
  """Total cost basis of this position."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountPredictionMarketsUnrealizedPnl(TypedDict):
  """Unrealized profit/loss on this position."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountSpotPositionsItemAverageEntryPrice(TypedDict):
  """Average price paid across all fills."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountSpotPositionsItemCostBasis(TypedDict):
  """Total cost basis of this position."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTotalBalance(TypedDict):
  """Total portfolio value."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTotalBalanceEquity(TypedDict):
  """Total balance, in shares."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTotalBalanceFiat(TypedDict):
  """Total balance, in fiat."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTotalCashEquivalentBalance(TypedDict):
  """Total cash-equivalent balance."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTotalCryptoBalance(TypedDict):
  """Total crypto balance."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTotalEquitiesBalance(TypedDict):
  """Total equities balance."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTotalFuturesBalance(TypedDict):
  """Total futures balance."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountUnrealizedPnlRawCurrency(TypedDict):
  """Value in the position's raw (quote) currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountUnrealizedPnlUserNativeCurrency(TypedDict):
  """Value in the user's native currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountVwapRawCurrency(TypedDict):
  """Value in the position's raw (quote) currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountVwapUserNativeCurrency(TypedDict):
  """Value in the user's native currency."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class FuturesPosition(TypedDict):
  """One open dated futures position."""

  product_id: NotRequired[str]
  """Futures product id."""
  contract_size: NotRequired[str]
  """Size of one contract."""
  side: NotRequired[
    Literal[
      'FUTURES_POSITION_SIDE_UNSPECIFIED',
      'FUTURES_POSITION_SIDE_LONG',
      'FUTURES_POSITION_SIDE_SHORT',
    ]
  ]
  """Long or short."""
  amount: NotRequired[str]
  """Position size, in contracts."""
  avg_entry_price: NotRequired[str]
  """Average entry price."""
  current_price: NotRequired[str]
  """Current contract price."""
  unrealized_pnl: NotRequired[str]
  """Unrealized profit/loss on this position."""
  expiry: NotRequired[str]
  """RFC3339 contract expiry time."""
  underlying_asset: NotRequired[str]
  """Symbol of the underlying asset."""
  asset_img_url: NotRequired[str]
  """URL of the underlying asset's icon."""
  product_name: NotRequired[str]
  """Display name of the contract."""
  venue: NotRequired[str]
  """Venue the contract trades on."""
  notional_value: NotRequired[str]
  """Total notional value of this position."""
  asset_color: NotRequired[str]
  """Display color associated with this asset."""
  last_traded_at: NotRequired[str]
  """RFC3339 time this contract last traded."""
  roll_date: NotRequired[str]
  """RFC3339 date this contract rolls to the next expiry."""
  price_increment: NotRequired[str]
  """Minimum price increment for this contract."""
  price_precision: NotRequired[int]
  """Number of decimal places in this contract's price."""


class Portfolio(TypedDict):
  """The portfolio's identity."""

  name: str
  """Portfolio display name."""
  uuid: str
  """Portfolio id."""
  type: Literal['UNDEFINED', 'DEFAULT', 'CONSUMER', 'INTX']
  """Portfolio classification."""
  deleted: bool
  """Whether the portfolio has been deleted."""


class DualCurrencyAmountImNotional(TypedDict):
  """Notional value backing initial margin, in the user's native currency and in the position's raw currency."""

  userNativeCurrency: NotRequired[AmountImNotionalUserNativeCurrency]
  rawCurrency: NotRequired[AmountImNotionalRawCurrency]


class DualCurrencyAmountLiquidationPrice(TypedDict):
  """Price at which this position is liquidated, in the user's native currency and in the position's raw currency."""

  userNativeCurrency: NotRequired[AmountLiquidationPriceUserNativeCurrency]
  rawCurrency: NotRequired[AmountLiquidationPriceRawCurrency]


class DualCurrencyAmountMarkPrice(TypedDict):
  """Current mark price, in the user's native currency and in the position's raw currency."""

  userNativeCurrency: NotRequired[AmountMarkPriceUserNativeCurrency]
  rawCurrency: NotRequired[AmountMarkPriceRawCurrency]


class DualCurrencyAmountMmNotional(TypedDict):
  """Notional value backing maintenance margin, in the user's native currency and in the position's raw currency."""

  userNativeCurrency: NotRequired[AmountMmNotionalUserNativeCurrency]
  rawCurrency: NotRequired[AmountMmNotionalRawCurrency]


class DualCurrencyAmountPositionNotional(TypedDict):
  """Total notional value of this position, in the user's native currency and in the position's raw currency."""

  userNativeCurrency: NotRequired[AmountPositionNotionalUserNativeCurrency]
  rawCurrency: NotRequired[AmountPositionNotionalRawCurrency]


class DualCurrencyAmountUnrealizedPnl(TypedDict):
  """Unrealized profit/loss, in the user's native currency and in the position's raw currency."""

  userNativeCurrency: NotRequired[AmountUnrealizedPnlUserNativeCurrency]
  rawCurrency: NotRequired[AmountUnrealizedPnlRawCurrency]


class DualCurrencyAmountVwap(TypedDict):
  """Volume-weighted average price, in the user's native currency and in the position's raw currency."""

  userNativeCurrency: NotRequired[AmountVwapUserNativeCurrency]
  rawCurrency: NotRequired[AmountVwapRawCurrency]


class EquityPosition(TypedDict):
  """One open equity position."""

  cbrn: NotRequired[str]
  """CBRN identifier of the equity."""
  account_uuid: NotRequired[str]
  """Id of the account holding this position."""
  total_balance_fiat: NotRequired[AmountTotalBalanceFiat]
  total_balance_equity: NotRequired[AmountTotalBalanceEquity]
  available_to_trade_equity: NotRequired[AmountAvailableToTradeEquity]
  available_to_trade_fiat: NotRequired[AmountAvailableToTradeFiat]
  account_type: NotRequired[
    Literal[
      'ACCOUNT_TYPE_UNKNOWN_UNSPECIFIED',
      'ACCOUNT_TYPE_WALLET',
      'ACCOUNT_TYPE_FIAT',
      'ACCOUNT_TYPE_VAULT',
      'ACCOUNT_TYPE_COLLATERAL',
      'ACCOUNT_TYPE_DEFI_YIELD',
      'ACCOUNT_TYPE_LOAN_MANAGEMENT',
      'ACCOUNT_TYPE_MULTISIG',
      'ACCOUNT_TYPE_MULTISIG_VAULT',
      'ACCOUNT_TYPE_DERIVATIVES_TRANSFER',
      'ACCOUNT_TYPE_DERIVATIVES_EQUITY',
      'ACCOUNT_TYPE_STAKED_FUNDS',
      'ACCOUNT_TYPE_PERP_FUTURES',
      'ACCOUNT_TYPE_PERP_FUTURES_ISOLATED',
      'ACCOUNT_TYPE_LENT_FUNDS',
      'ACCOUNT_TYPE_PERP_FUTURES_COLLATERAL',
      'ACCOUNT_TYPE_DERIVATIVES_CASH',
      'ACCOUNT_TYPE_CLAWBACK_DEBT',
      'ACCOUNT_TYPE_SUSPENSE_GEOFENCE',
      'ACCOUNT_TYPE_RETAIL_DEFI_LEND',
      'ACCOUNT_TYPE_DEFI_BORROW_COLLATERAL',
      'ACCOUNT_TYPE_FIAT_SAVINGS',
      'ACCOUNT_TYPE_RAISE_INVESTMENTS',
      'ACCOUNT_TYPE_CCM_EQUITY',
      'ACCOUNT_TYPE_PREDICTION_MARKETS_TRANSFER',
      'ACCOUNT_TYPE_PREDICTION_MARKETS_EQUITY',
      'ACCOUNT_TYPE_PREDICTION_MARKETS_CFM',
      'ACCOUNT_TYPE_CREDIT_CARD_COLLATERAL',
    ]
  ]
  """Type of account holding this position."""
  allocation: NotRequired[float]
  """Fraction of the portfolio this position represents."""
  cost_basis: NotRequired[AmountEquityPositionsItemCostBasis]
  average_entry_price: NotRequired[AmountEquityPositionsItemAverageEntryPrice]
  unrealized_pnl: NotRequired[AmountItemUnrealizedPnl]


class PortfolioBalances(TypedDict):
  """Aggregate balances across the portfolio."""

  total_balance: NotRequired[AmountTotalBalance]
  total_futures_balance: NotRequired[AmountTotalFuturesBalance]
  total_cash_equivalent_balance: NotRequired[AmountTotalCashEquivalentBalance]
  total_crypto_balance: NotRequired[AmountTotalCryptoBalance]
  futures_unrealized_pnl: NotRequired[AmountFuturesUnrealizedPnl]
  perp_unrealized_pnl: NotRequired[AmountPerpUnrealizedPnl]
  total_equities_balance: NotRequired[AmountTotalEquitiesBalance]


class PredictionMarketsPositionDetail(TypedDict):
  """Prediction-market-specific position detail."""

  side: NotRequired[
    Literal[
      'PREDICTION_MARKETS_POSITION_SIDE_UNSPECIFIED',
      'PREDICTION_MARKETS_POSITION_SIDE_LONG',
      'PREDICTION_MARKETS_POSITION_SIDE_SHORT',
    ]
  ]
  """Long (YES) or short (NO) side of the position."""
  last_traded_at: NotRequired[str]
  """RFC3339 time this market last traded."""
  average_entry_price: NotRequired[AmountPredictionMarketsAverageEntryPrice]
  current_price: NotRequired[AmountCurrentPrice]
  unrealized_pnl: NotRequired[AmountPredictionMarketsUnrealizedPnl]
  notional_value: NotRequired[AmountNotionalValue]
  cost_basis: NotRequired[AmountPredictionMarketsCostBasis]
  contracts_owned: NotRequired[str]
  """Number of contracts owned."""
  quote_cbrn: NotRequired[str]
  """CBRN identifier of the quote instrument."""


class SpotPosition(TypedDict):
  """One held spot asset."""

  asset: NotRequired[str]
  """Asset symbol."""
  account_uuid: NotRequired[str]
  """Id of the account holding this asset."""
  total_balance_fiat: NotRequired[float]
  """Total balance, in fiat."""
  total_balance_crypto: NotRequired[float]
  """Total balance, in the asset itself."""
  available_to_trade_fiat: NotRequired[float]
  """Balance available to trade, in fiat."""
  allocation: NotRequired[float]
  """Fraction of the portfolio this position represents."""
  cost_basis: NotRequired[AmountSpotPositionsItemCostBasis]
  asset_img_url: NotRequired[str]
  """URL of the asset's icon."""
  is_cash: NotRequired[bool]
  """Whether this position is a cash/fiat balance rather than crypto."""
  average_entry_price: NotRequired[AmountSpotPositionsItemAverageEntryPrice]
  asset_uuid: NotRequired[str]
  """Id of the asset."""
  available_to_trade_crypto: NotRequired[float]
  """Balance available to trade, in the asset itself."""
  unrealized_pnl: NotRequired[float]
  """Unrealized profit/loss on this position."""
  available_to_transfer_fiat: NotRequired[float]
  """Balance available to transfer, in fiat."""
  available_to_transfer_crypto: NotRequired[float]
  """Balance available to transfer, in the asset itself."""
  asset_color: NotRequired[str]
  """Display color associated with this asset."""
  account_type: NotRequired[
    Literal[
      'ACCOUNT_TYPE_UNKNOWN_UNSPECIFIED',
      'ACCOUNT_TYPE_WALLET',
      'ACCOUNT_TYPE_FIAT',
      'ACCOUNT_TYPE_VAULT',
      'ACCOUNT_TYPE_COLLATERAL',
      'ACCOUNT_TYPE_DEFI_YIELD',
      'ACCOUNT_TYPE_LOAN_MANAGEMENT',
      'ACCOUNT_TYPE_MULTISIG',
      'ACCOUNT_TYPE_MULTISIG_VAULT',
      'ACCOUNT_TYPE_DERIVATIVES_TRANSFER',
      'ACCOUNT_TYPE_DERIVATIVES_EQUITY',
      'ACCOUNT_TYPE_STAKED_FUNDS',
      'ACCOUNT_TYPE_PERP_FUTURES',
      'ACCOUNT_TYPE_PERP_FUTURES_ISOLATED',
      'ACCOUNT_TYPE_LENT_FUNDS',
      'ACCOUNT_TYPE_PERP_FUTURES_COLLATERAL',
      'ACCOUNT_TYPE_DERIVATIVES_CASH',
      'ACCOUNT_TYPE_CLAWBACK_DEBT',
      'ACCOUNT_TYPE_SUSPENSE_GEOFENCE',
      'ACCOUNT_TYPE_RETAIL_DEFI_LEND',
      'ACCOUNT_TYPE_DEFI_BORROW_COLLATERAL',
      'ACCOUNT_TYPE_FIAT_SAVINGS',
      'ACCOUNT_TYPE_RAISE_INVESTMENTS',
      'ACCOUNT_TYPE_CCM_EQUITY',
      'ACCOUNT_TYPE_PREDICTION_MARKETS_TRANSFER',
      'ACCOUNT_TYPE_PREDICTION_MARKETS_EQUITY',
      'ACCOUNT_TYPE_PREDICTION_MARKETS_CFM',
      'ACCOUNT_TYPE_CREDIT_CARD_COLLATERAL',
    ]
  ]
  """Type of account holding this position."""
  funding_pnl: NotRequired[float]
  """Profit/loss from funding payments."""
  available_to_send_fiat: NotRequired[float]
  """Balance available to send, in fiat."""
  available_to_send_crypto: NotRequired[float]
  """Balance available to send, in the asset itself."""


class PerpPosition(TypedDict):
  """One open perpetual futures position."""

  product_id: NotRequired[str]
  """Perpetual futures product id."""
  product_uuid: NotRequired[str]
  """Id of the product."""
  symbol: NotRequired[str]
  """Display symbol."""
  asset_image_url: NotRequired[str]
  """URL of the underlying asset's icon."""
  vwap: NotRequired[DualCurrencyAmountVwap]
  position_side: NotRequired[
    Literal[
      'FUTURES_POSITION_SIDE_UNSPECIFIED',
      'FUTURES_POSITION_SIDE_LONG',
      'FUTURES_POSITION_SIDE_SHORT',
    ]
  ]
  """Long or short."""
  net_size: NotRequired[str]
  """Net position size."""
  buy_order_size: NotRequired[str]
  """Total size of open buy orders on this product."""
  sell_order_size: NotRequired[str]
  """Total size of open sell orders on this product."""
  im_contribution: NotRequired[str]
  """This position's contribution to initial margin."""
  unrealized_pnl: NotRequired[DualCurrencyAmountUnrealizedPnl]
  mark_price: NotRequired[DualCurrencyAmountMarkPrice]
  liquidation_price: NotRequired[DualCurrencyAmountLiquidationPrice]
  leverage: NotRequired[str]
  """Leverage applied to this position."""
  im_notional: NotRequired[DualCurrencyAmountImNotional]
  mm_notional: NotRequired[DualCurrencyAmountMmNotional]
  position_notional: NotRequired[DualCurrencyAmountPositionNotional]
  margin_type: NotRequired[
    Literal['MARGIN_TYPE_UNSPECIFIED', 'MARGIN_TYPE_CROSS', 'MARGIN_TYPE_ISOLATED']
  ]
  """Cross or isolated margin."""
  liquidation_buffer: NotRequired[str]
  """Distance from the current mark price to the liquidation price."""
  liquidation_percentage: NotRequired[str]
  """Liquidation buffer, as a percentage."""
  asset_color: NotRequired[str]
  """Display color associated with this asset."""


class PredictionMarketsPosition(TypedDict):
  """One open prediction-market position."""

  product_type: NotRequired[
    Literal[
      'PRODUCT_TYPE_UNSPECIFIED',
      'PRODUCT_TYPE_ALL',
      'PRODUCT_TYPE_SPOT',
      'PRODUCT_TYPE_FCM_FUTURES',
      'PRODUCT_TYPE_PERP_FUTURES',
      'PRODUCT_TYPE_INTX_SPOT',
      'PRODUCT_TYPE_DEX',
      'PRODUCT_TYPE_EQUITY',
      'PRODUCT_TYPE_PREDICTION_MARKETS',
      'PRODUCT_TYPE_COMPOSITE_CRYPTO',
    ]
  ]
  """Class of the product this position is in."""
  cbrn: NotRequired[str]
  """CBRN identifier of the prediction market."""
  prediction_markets: NotRequired[PredictionMarketsPositionDetail]


class PortfolioBreakdown(TypedDict):
  """The portfolio breakdown."""

  portfolio: Portfolio
  portfolio_balances: PortfolioBalances
  spot_positions: NotRequired[list[SpotPosition]]
  """Open spot asset positions."""
  perp_positions: NotRequired[list[PerpPosition]]
  """Open perpetual futures positions."""
  futures_positions: NotRequired[list[FuturesPosition]]
  """Open dated (expiring) futures positions."""
  prediction_markets_positions: NotRequired[list[PredictionMarketsPosition]]
  """Open prediction-market positions."""
  equity_positions: NotRequired[list[EquityPosition]]
  """Open equity positions."""


class GetPortfolioBreakdownResponse(TypedDict):
  breakdown: PortfolioBreakdown


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /api/v3/brokerage/portfolios/{portfolio_uuid}`."""

  async def get(
    self,
    portfolio_uuid: str,
    *,
    currency: str | None = None,
  ) -> GetPortfolioBreakdownResponse:
    """Get the full breakdown of a portfolio: its balances and every open position, by asset class.

    Args:
      portfolio_uuid: The id of the portfolio to fetch.
      currency: Currency to express fiat-denominated values in, e.g. `USD`.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/portfolios/get-portfolio-breakdown)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    return await self.authed_request(
      'GET',
      f'/api/v3/brokerage/portfolios/{portfolio_uuid}',
      params=params,
      validator=validator(GetPortfolioBreakdownResponse),
    )
