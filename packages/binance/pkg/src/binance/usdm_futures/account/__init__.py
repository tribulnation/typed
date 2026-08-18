from .account_config import AccountConfig
from .account_v2 import AccountV2
from .account_v3 import AccountV3
from .api_trading_status import ApiTradingStatus
from .balance_v2 import BalanceV2
from .balance_v3 import BalanceV3
from .fee_burn import FeeBurn
from .income import Income
from .leverage_bracket import LeverageBracket
from .listen_key_close import ListenKeyClose
from .listen_key_keepalive import ListenKeyKeepalive
from .listen_key_start import ListenKeyStart
from .pm_account_info import PmAccountInfo
from .rate_limit_order import RateLimitOrder
from .symbol_config import SymbolConfig
from .toggle_fee_burn import ToggleFeeBurn


class Account(
  AccountConfig,
  AccountV2,
  AccountV3,
  ApiTradingStatus,
  BalanceV2,
  BalanceV3,
  FeeBurn,
  Income,
  LeverageBracket,
  ListenKeyClose,
  ListenKeyKeepalive,
  ListenKeyStart,
  PmAccountInfo,
  RateLimitOrder,
  SymbolConfig,
  ToggleFeeBurn,
):
  """Binance account endpoints."""
