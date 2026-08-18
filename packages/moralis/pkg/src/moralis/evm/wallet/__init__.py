"""Moralis EVM wallet endpoint group."""

from .history import History as History
from .token_balances import TokenBalances as TokenBalances
from .token_transfers import TokenTransfers as TokenTransfers


class Wallet(
  History,
  TokenBalances,
  TokenTransfers,
):
  """Grouped Moralis EVM wallet endpoints."""
