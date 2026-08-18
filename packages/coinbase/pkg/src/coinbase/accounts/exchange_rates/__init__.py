from dataclasses import dataclass
from .list import List


@dataclass(frozen=True, kw_only=True)
class ExchangeRates(List):
  """`exchange_rates` endpoints."""
