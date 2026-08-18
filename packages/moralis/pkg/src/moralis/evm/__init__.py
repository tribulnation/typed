"""Moralis EVM API group."""

from moralis.core import Router
from .wallet import Wallet
from .token import Token

class Evm(Router):
  """Moralis EVM APIs."""
  wallet: Wallet
  """Wallet history, transfer, and balance endpoints."""
  token: Token
  """Token metadata endpoints."""