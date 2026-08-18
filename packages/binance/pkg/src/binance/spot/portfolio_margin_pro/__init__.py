from .asset_collection import AssetCollection
from .asset_index_price import AssetIndexPrice
from .asset_leverage import AssetLeverage
from .auto_collection import AutoCollection
from .auto_repay_futures_status import AutoRepayFuturesStatus
from .balance import Balance
from .bankruptcy_loan_amount import BankruptcyLoanAmount
from .bankruptcy_loan_repay import BankruptcyLoanRepay
from .bankruptcy_loan_repay_history import BankruptcyLoanRepayHistory
from .bnb_transfer import BnbTransfer
from .collateral_rate import CollateralRate
from .delete_margin_call_level import DeleteMarginCallLevel
from .delta_mode import DeltaMode
from .earn_asset_balance import EarnAssetBalance
from .earn_asset_transfer import EarnAssetTransfer
from .info import Info
from .margin_call_level import MarginCallLevel
from .negative_balance_interest_history import NegativeBalanceInterestHistory
from .repay_futures_negative_balance import RepayFuturesNegativeBalance
from .set_auto_repay_futures_status import SetAutoRepayFuturesStatus
from .set_delta_mode import SetDeltaMode
from .set_margin_call_level import SetMarginCallLevel
from .span_info import SpanInfo
from .tiered_collateral_rate import TieredCollateralRate


class PortfolioMarginPro(
  AssetCollection,
  AssetIndexPrice,
  AssetLeverage,
  AutoCollection,
  AutoRepayFuturesStatus,
  Balance,
  BankruptcyLoanAmount,
  BankruptcyLoanRepay,
  BankruptcyLoanRepayHistory,
  BnbTransfer,
  CollateralRate,
  DeleteMarginCallLevel,
  DeltaMode,
  EarnAssetBalance,
  EarnAssetTransfer,
  Info,
  MarginCallLevel,
  NegativeBalanceInterestHistory,
  RepayFuturesNegativeBalance,
  SetAutoRepayFuturesStatus,
  SetDeltaMode,
  SetMarginCallLevel,
  SpanInfo,
  TieredCollateralRate,
):
  """Binance portfolio_margin_pro endpoints."""
