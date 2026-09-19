"""Kraken Futures chart transport for bare catalogue and candle payloads."""

from ..core.transport.public import PublicHttpClient


class ChartsHttpClient(PublicHttpClient):
  """Use the chart API's bare JSON payloads and HTTP status errors."""
