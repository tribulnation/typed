from .access_log import AccessLog
from .changes_by_instrument import ChangesByInstrument
from .changes_by_kind_currency import ChangesByKindCurrency
from .combo_trades_by_instrument import ComboTradesByInstrument
from .combo_trades_by_kind_currency import ComboTradesByKindCurrency
from .lock import Lock
from .mmp_trigger import MmpTrigger
from .orders_by_instrument import OrdersByInstrument
from .orders_by_instrument_raw import OrdersByInstrumentRaw
from .orders_by_kind_currency import OrdersByKindCurrency
from .orders_by_kind_currency_raw import OrdersByKindCurrencyRaw
from .portfolio import Portfolio
from .trades_by_instrument import TradesByInstrument
from .trades_by_kind_currency import TradesByKindCurrency


class User(
  AccessLog,
  ChangesByInstrument,
  ChangesByKindCurrency,
  ComboTradesByInstrument,
  ComboTradesByKindCurrency,
  Lock,
  MmpTrigger,
  OrdersByInstrument,
  OrdersByInstrumentRaw,
  OrdersByKindCurrency,
  OrdersByKindCurrencyRaw,
  Portfolio,
  TradesByInstrument,
  TradesByKindCurrency,
):
  """User endpoints."""
