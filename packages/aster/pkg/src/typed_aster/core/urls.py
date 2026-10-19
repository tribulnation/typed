"""Base URLs of every Aster surface, per network.

Aster Chain REST, its JSON-RPC and BAPI have no testnet: they always resolve to mainnet.
"""

from typing_extensions import Literal, TypedDict

Surface = Literal['futures', 'spot', 'prediction']

REST_HOSTS: dict[Surface, tuple[str, str]] = {
  'futures': ('https://fapi.asterdex.com', 'https://fapi.asterdex-testnet.com'),
  'spot': ('https://sapi.asterdex.com', 'https://sapi.asterdex-testnet.com'),
  'prediction': ('https://papi.asterdex.com', 'https://papi.asterdex-testnet.com'),
}
"""`(mainnet, testnet)` REST hosts."""

REST_PREFIXES: dict[Surface, str] = {
  'futures': '/fapi/v3',
  'spot': '/api/v3',
  'prediction': '/api/v3',
}

STREAM_HOSTS: dict[Surface, tuple[str, str]] = {
  'futures': ('wss://fstream.asterdex.com', 'wss://fstream.asterdex-testnet.com'),
  'spot': ('wss://sstream.asterdex.com', 'wss://sstream.asterdex-testnet.com'),
  'prediction': ('wss://pstream.asterdex.com', 'wss://pstream.asterdex-testnet.com'),
}
"""`(mainnet, testnet)` WebSocket hosts."""

CHAIN_REST_URL = 'https://chainapi.asterdex.com/aster-chain/v3'
CHAIN_RPC_URL = 'https://tapi.asterdex.com/info'
BAPI_URL = 'https://www.asterdex.com/bapi'


def rest_url(surface: Surface, *, mainnet: bool) -> str:
  """REST base URL of `surface`, e.g. `https://fapi.asterdex.com/fapi/v3`."""
  host = REST_HOSTS[surface][0 if mainnet else 1]
  return host + REST_PREFIXES[surface]


def streams_url(surface: Surface, *, mainnet: bool) -> str:
  """Combined market-data stream URL of `surface`."""
  return STREAM_HOSTS[surface][0 if mainnet else 1] + '/stream'


def user_stream_url(surface: Surface, *, mainnet: bool) -> str:
  """User-data stream base URL of `surface`; the listenKey is appended as a path segment."""
  return STREAM_HOSTS[surface][0 if mainnet else 1] + '/ws'


class SurfaceUrls(TypedDict, total=False):
  """URL overrides of one trading surface; a missing key keeps the network's default."""

  rest: str
  """REST base URL, version prefix included, e.g. `https://fapi.asterdex.com/fapi/v3`."""
  streams: str
  """Combined market-data stream URL, e.g. `wss://fstream.asterdex.com/stream`."""
  user_stream: str
  """User-data stream base URL, e.g. `wss://fstream.asterdex.com/ws`; the listenKey is
  appended as a path segment."""


class ChainUrls(TypedDict, total=False):
  """URL overrides of Aster Chain; a missing key keeps the default."""

  rest: str
  """REST base URL, e.g. `https://chainapi.asterdex.com/aster-chain/v3`."""
  rpc: str
  """JSON-RPC URL, e.g. `https://tapi.asterdex.com/info`."""


class Urls(TypedDict, total=False):
  """Base URL overrides, per surface. Each one takes precedence over the URL the
  `mainnet` flag selects; a missing key keeps it."""

  futures: SurfaceUrls
  spot: SurfaceUrls
  prediction: SurfaceUrls
  chain: ChainUrls
  bapi: str
  """BAPI base URL, e.g. `https://www.asterdex.com/bapi`."""
