"""EVEDEX environments: hosts, WebSocket channel prefix and EIP-712 chain id of each."""

from typing_extensions import Literal, TypeAliasType
from dataclasses import dataclass

Environment = TypeAliasType('Environment', Literal['prod', 'demo'])
"""`prod` is the live exchange (`evedex.com`); `demo` the paper-trading one (`evedex.io`)."""


@dataclass(frozen=True, kw_only=True)
class EnvironmentProfile:
  """Everything that differs between two EVEDEX deployments."""

  exchange_url: str
  """Exchange (trading) REST API."""
  auth_url: str
  """Auth REST API: SIWE login, token refresh, API keys."""
  market_data_url: str
  """Market-data REST API: candle history."""
  ws_url: str
  """Centrifugo WebSocket endpoint."""
  channel_prefix: str
  """Namespace of every exchange channel (`<prefix>:heartbeat`). Market-data channels use
  the fixed `market-data` namespace instead."""
  chain_id: int
  """Chain id of the EIP-712 domain and of the SIWE message."""
  env_prefix: str
  """Prefix of the environment variables holding this deployment's credentials."""


ENVIRONMENTS: dict[Environment, EnvironmentProfile] = {
  'prod': EnvironmentProfile(
    exchange_url='https://trading-api.evedex.com',
    auth_url='https://auth-api.evedex.com',
    market_data_url='https://market-data-api.evedex.com',
    ws_url='wss://ws.evedex.com/connection/websocket',
    channel_prefix='futures-perp',
    chain_id=42161,
    env_prefix='EVEDEX_',
  ),
  'demo': EnvironmentProfile(
    exchange_url='https://trading-api.evedex.io',
    auth_url='https://auth-api.evedex.io',
    market_data_url='https://market-data-api.evedex.io',
    ws_url='wss://ws.evedex.io/connection/websocket',
    channel_prefix='futures-perp-beta',
    chain_id=421614,
    env_prefix='EVEDEX_DEMO_',
  ),
}
"""The public deployments. Demo's channel prefix is `futures-perp-beta` (verified live
2026-11-19: `futures-perp-demo:*` answers `unknown channel`), and its chain id is Arbitrum
Sepolia's."""
