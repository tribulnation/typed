from .session_logon import SessionLogon
from .session_logout import SessionLogout
from .session_status import SessionStatus


class General(SessionLogon, SessionLogout, SessionStatus):
  """Binance general endpoints."""
