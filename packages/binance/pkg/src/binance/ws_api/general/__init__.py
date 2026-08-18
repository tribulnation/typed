from .exchange_info import ExchangeInfoEndpoint
from .execution_rules import ExecutionRulesEndpoint
from .session_logon import SessionLogon
from .session_logout import SessionLogout
from .session_status import SessionStatusEndpoint
from .time import Time


class General(
  ExchangeInfoEndpoint,
  ExecutionRulesEndpoint,
  SessionLogon,
  SessionLogout,
  SessionStatusEndpoint,
  Time,
):
  """Binance general endpoints."""
