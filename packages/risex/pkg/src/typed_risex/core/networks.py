"""RISEx deployments: REST and WebSocket hosts, and the chain each one settles on."""

from typing_extensions import Literal, TypeAliasType
from dataclasses import dataclass

Network = TypeAliasType('Network', Literal['mainnet', 'testnet'])
"""A RISEx deployment: `mainnet` (RISE Mainnet, access-gated) or `testnet` (open)."""


@dataclass(frozen=True, kw_only=True)
class NetworkProfile:
  """Hosts and chain of one deployment."""

  name: Network
  """Deployment name."""
  api_url: str
  """REST base URL."""
  ws_url: str
  """WebSocket feed URL."""
  chain_id: int
  """RISE Chain id. Every EIP-712 signature commits to it through the domain, which the
  client fetches from the API and checks against this value before signing anything."""


NETWORKS: dict[Network, NetworkProfile] = {
  'mainnet': NetworkProfile(
    name='mainnet',
    api_url='https://api.rise.trade',
    ws_url='wss://ws.rise.trade/ws',
    chain_id=4153,
  ),
  'testnet': NetworkProfile(
    name='testnet',
    api_url='https://api.testnet.rise.trade',
    # The documented `wss://ws.testnet.rise.trade/ws` fails the TLS handshake (HTTP 525);
    # this host works, and needs the trailing slash.
    ws_url='wss://api.testnet.rise.trade/ws/',
    chain_id=11155931,
  ),
}
"""Every deployment, by name."""
