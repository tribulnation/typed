"""Bybit v5 HTTP endpoints."""

from bybit.core import Router
from .account import Account
from .market import Market


class Http(Router):
  """Bybit v5 HTTP endpoints."""

  market: Market
  account: Account
