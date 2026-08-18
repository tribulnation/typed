from dataclasses import dataclass
from .coinbase_one import CoinbaseOne


@dataclass(frozen=True, kw_only=True)
class Subscriptions(CoinbaseOne):
  """`subscriptions` endpoints."""
