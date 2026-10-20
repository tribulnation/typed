"""Extended's deployments: Starknet mainnet and Starknet Sepolia testnet.

Each network fixes its REST and stream hosts and its SNIP-12 signing domain together, so
a client can never sign for one network and send to the other.
"""

from typing_extensions import Literal, TypeAliasType
from dataclasses import dataclass

from .stark.messages import StarknetDomain

Network = TypeAliasType('Network', Literal['mainnet', 'testnet'])
"""An Extended deployment: `mainnet` (Starknet `SN_MAIN`) or `testnet` (Starknet Sepolia)."""


@dataclass(frozen=True, kw_only=True)
class NetworkProfile:
  """Hosts and signing domain of one deployment."""

  name: Network
  """Deployment name."""
  api_url: str
  """REST base URL, including the `/api/v1` prefix."""
  stream_url: str
  """WebSocket v1 base URL (one stream per connection, picked by path)."""
  domain: StarknetDomain
  """SNIP-12 domain every settlement signature is bound to (`GET /info/starknet`)."""
  env_prefix: str
  """Prefix of the environment variables credentials are read from."""


NETWORKS: dict[Network, NetworkProfile] = {
  'mainnet': NetworkProfile(
    name='mainnet',
    api_url='https://api.starknet.extended.exchange/api/v1',
    stream_url='wss://api.starknet.extended.exchange/stream.extended.exchange/v1',
    domain=StarknetDomain(chain_id='SN_MAIN'),
    env_prefix='EXTENDED',
  ),
  'testnet': NetworkProfile(
    name='testnet',
    api_url='https://api.starknet.sepolia.extended.exchange/api/v1',
    stream_url='wss://api.starknet.sepolia.extended.exchange/stream.extended.exchange/v1',
    domain=StarknetDomain(chain_id='SN_SEPOLIA'),
    env_prefix='EXTENDED_TESTNET',
  ),
}
"""Every deployment, by name."""
