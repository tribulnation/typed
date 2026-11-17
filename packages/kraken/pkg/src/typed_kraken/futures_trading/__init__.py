"""Authenticated Kraken Futures: signed REST trading and account reads, and the
WebSocket v1 feeds (books, fills, open orders, positions, balances)."""

from .client import FuturesEnvironment, KrakenFutures
