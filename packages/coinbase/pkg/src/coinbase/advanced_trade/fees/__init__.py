from dataclasses import dataclass
from .transaction_summary import TransactionSummary


@dataclass(frozen=True, kw_only=True)
class Fees(TransactionSummary):
  """`fees` endpoints."""
