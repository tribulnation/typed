"""Lighter network profiles: REST URL, WebSocket URL, chain id and explorer URL, picked together.

The chain id is not metadata: the signer mixes it into every transaction hash, so a client
must never pair one network's base URL with another network's chain id.
"""

from typing_extensions import Literal, TypeAliasType
from dataclasses import dataclass

Network = TypeAliasType(
  'Network', Literal['mainnet', 'testnet', 'robinhood', 'robinhood-testnet']
)
"""A Lighter deployment."""


@dataclass(frozen=True, kw_only=True)
class NetworkProfile:
  """Everything that differs between Lighter deployments."""

  api_url: str
  """Main REST API base URL (paths start with `/api/v1/`)."""
  ws_url: str
  """WebSocket stream URL."""
  chain_id: int
  """Lighter chain id, mixed into every transaction hash by the signer."""
  explorer_url: str | None
  """Explorer API base URL, or `None` when the deployment has no known explorer."""
  env_prefix: str
  """Prefix of this deployment's credential environment variables (`LIGHTER_TESTNET` reads
  `LIGHTER_TESTNET_ACCOUNT_INDEX`, `LIGHTER_TESTNET_API_PRIVATE_KEY`, ...)."""


NETWORKS: dict[Network, NetworkProfile] = {
  'mainnet': NetworkProfile(
    api_url='https://mainnet.zklighter.elliot.ai',
    ws_url='wss://mainnet.zklighter.elliot.ai/stream',
    chain_id=304,
    explorer_url='https://explorer.elliot.ai/api',
    env_prefix='LIGHTER',
  ),
  'testnet': NetworkProfile(
    api_url='https://testnet.zklighter.elliot.ai',
    ws_url='wss://testnet.zklighter.elliot.ai/stream',
    chain_id=300,
    explorer_url='https://testnet.explorer.elliot.ai/api',
    env_prefix='LIGHTER_TESTNET',
  ),
  'robinhood': NetworkProfile(
    api_url='https://api.rh.lighter.xyz',
    ws_url='wss://api.rh.lighter.xyz/stream',
    chain_id=466324,
    explorer_url=None,
    env_prefix='LIGHTER_ROBINHOOD',
  ),
  'robinhood-testnet': NetworkProfile(
    api_url='https://api.rh-testnet.lighter.xyz',
    ws_url='wss://api.rh-testnet.lighter.xyz/stream',
    chain_id=300,
    explorer_url=None,
    env_prefix='LIGHTER_ROBINHOOD_TESTNET',
  ),
}
"""Every known deployment's profile."""

BRIDGE_URL = 'https://bridge.lighter.xyz'
"""Deposit bridge (universal deposit addresses) base URL, shared by every deployment."""
