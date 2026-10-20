"""GRVT environments: hosts and EIP-712 chain ids."""

from dataclasses import dataclass

from typing_extensions import Literal, TypeAliasType

Environment = TypeAliasType('Environment', Literal['prod', 'testnet', 'staging'])
"""GRVT deployment to connect to."""

DOMAINS: dict[Environment, str] = {
  'prod': 'grvt.io',
  'testnet': 'testnet.grvt.io',
  'staging': 'staging.gravitymarkets.io',
}
"""Domain every host family of an environment lives under."""

CHAIN_IDS: dict[Environment, int] = {'prod': 325, 'testnet': 326, 'staging': 327}
"""GRVT L2 chain id, the `chainId` of every EIP-712 domain.

Staging is `327` per the docs, the TypeScript SDK and the Python SDK's signing module (the
Python SDK's environment module says `328`, which disagrees with its own signer).
"""


@dataclass(frozen=True, kw_only=True)
class Hosts:
  """Base URLs of one environment's three host families."""

  market_data: str
  """Market-data gateway HTTP base URL (public RPCs, `GET /time`)."""
  market_data_ws: str
  """Market-data gateway JSON-RPC WebSocket URL (full encoding)."""
  trades: str
  """Trading gateway HTTP base URL (authenticated RPCs)."""
  trades_ws: str
  """Trading gateway JSON-RPC WebSocket URL (full encoding)."""
  edge: str
  """Edge host base URL (login, referral, deposit, bridge)."""
  chain_id: int
  """EIP-712 domain chain id."""

  @classmethod
  def of(cls, env: Environment) -> 'Hosts':
    """Resolve the hosts of a GRVT environment.

    Args:
      env: Environment to resolve.
    """
    domain = DOMAINS[env]
    return cls(
      market_data=f'https://market-data.{domain}',
      market_data_ws=f'wss://market-data.{domain}/ws/full',
      trades=f'https://trades.{domain}',
      trades_ws=f'wss://trades.{domain}/ws/full',
      edge=f'https://edge.{domain}',
      chain_id=CHAIN_IDS[env],
    )
