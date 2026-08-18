from .lead_status import LeadStatus
from .lead_symbol import LeadSymbol


class Futures(LeadStatus, LeadSymbol):
  """Binance futures endpoints."""
