"""Nado deployments: every host, plus the EIP-712 signing domain, of each network."""

from typing_extensions import Literal, TypeAliasType
from dataclasses import dataclass

Network = TypeAliasType('Network', Literal['mainnet', 'testnet'])
"""A Nado deployment: `mainnet` (Ink) or `testnet` (Ink Sepolia)."""


@dataclass(frozen=True, kw_only=True)
class NetworkProfile:
  """Hosts and signing domain of one Nado deployment.

  Build one by hand only to point the client somewhere else (a local mock server, say);
  `NETWORKS` holds the real deployments.
  """

  name: str
  """Deployment name, used in error messages."""
  chain_id: int
  """EIP-712 `chainId`: Ink (57073) or Ink Sepolia (763373)."""
  endpoint_address: str
  """The Endpoint contract: the EIP-712 `verifyingContract` of every signed payload except
  orders, which verify against `address(product_id)`."""
  gateway_url: str
  """Gateway REST v1 base: `/query`, `/edge/query` and `/execute` hang off it."""
  gateway_ws_url: str
  """Gateway WebSocket v1 (serial: one request in flight per connection)."""
  subscriptions_url: str
  """Subscriptions WebSocket."""
  trigger_url: str
  """Trigger service base: `/query` and `/execute` hang off it."""
  archive_url: str
  """Archive (indexer) v1: every query is a `POST` to this URL."""
  rewards_url: str
  """Rewards v1: every query is a `POST` to this URL."""
  gateway_v2_url: str
  """Gateway REST v2 (market data, bare JSON)."""
  archive_v2_url: str
  """Archive REST v2 (market data, bare JSON)."""
  env_prefix: str
  """Prefix of the environment variables credentials are read from."""


def unified(
  name: str, *, host: str, chain_id: int, endpoint_address: str, env_prefix: str
) -> NetworkProfile:
  """A profile on the unified host (`api.{prod,test}.nado.xyz`), where every service hangs
  off one domain.

  Args:
    name: Deployment name.
    host: The unified API host, without scheme.
    chain_id: EIP-712 chain id.
    endpoint_address: The Endpoint contract address.
    env_prefix: Prefix of the credential environment variables.
  """
  return NetworkProfile(
    name=name,
    chain_id=chain_id,
    endpoint_address=endpoint_address,
    gateway_url=f'https://{host}/gateway/v1',
    gateway_ws_url=f'wss://{host}/gateway/v1/ws',
    subscriptions_url=f'wss://{host}/gateway/v1/subscribe',
    trigger_url=f'https://{host}/trigger/v1',
    archive_url=f'https://{host}/archive/v1',
    rewards_url=f'https://{host}/rewards/v1',
    gateway_v2_url=f'https://{host}/gateway/v2',
    archive_v2_url=f'https://{host}/archive/v2',
    env_prefix=env_prefix,
  )


NETWORKS: dict[str, NetworkProfile] = {
  'mainnet': unified(
    'mainnet',
    host='api.prod.nado.xyz',
    chain_id=57073,
    endpoint_address='0x05ec92D78ED421f3D3Ada77FFdE167106565974E',
    env_prefix='NADO_',
  ),
  'testnet': unified(
    'testnet',
    host='api.test.nado.xyz',
    chain_id=763373,
    endpoint_address='0x698D87105274292B5673367DEC81874Ce3633Ac2',
    env_prefix='NADO_TESTNET_',
  ),
}
"""The real deployments. Chain ids and Endpoint addresses match the live `contracts` query
of each gateway."""
