"""Hyperliquid network domains, and the per-transport URL resolution every surface
shares: `info` and `exchange` (HTTP or the shared WebSocket connection) and `streams`
(WebSocket only) all key off the same mainnet/testnet domain.
"""

HYPERLIQUID_MAINNET = 'api.hyperliquid.xyz'
HYPERLIQUID_TESTNET = 'api.hyperliquid-testnet.xyz'


def http_base_url(mainnet: bool = True) -> str:
  """Resolve the HTTP API root shared by `info` and `exchange`."""
  domain = HYPERLIQUID_MAINNET if mainnet else HYPERLIQUID_TESTNET
  return f'https://{domain}'


def ws_url(mainnet: bool = True) -> str:
  """Resolve the WebSocket URL shared by `info`, `exchange`, and `streams`."""
  domain = HYPERLIQUID_MAINNET if mainnet else HYPERLIQUID_TESTNET
  return f'wss://{domain}/ws'
