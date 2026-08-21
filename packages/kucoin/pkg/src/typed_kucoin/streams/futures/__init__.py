"""Channels on the Futures instance -- one physical connection, see `SocketStreamClient`."""

from .market import Market
from .private import Private


class FuturesChannels(Market, Private):
  """Public and private channels on the Futures instance -- one physical connection
  serves both, see `SocketStreamClient`."""
