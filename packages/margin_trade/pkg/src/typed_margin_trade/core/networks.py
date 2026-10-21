"""Margin Trade deployments: each one's HTTP host, WebSocket URL and envelope network code,
always picked together so a host and a network code can never be mixed.
"""

from typing_extensions import Literal, TypeAliasType
from dataclasses import dataclass

NetworkCode = TypeAliasType('NetworkCode', Literal['m', 't'])
"""Network code signed into every envelope (`n`): `m` mainnet, `t` testnet."""


@dataclass(frozen=True, kw_only=True)
class NetworkProfile:
  """Everything that differs between mainnet and testnet."""

  api_url: str
  """REST base URL (`/info`, `/exchange`, `/user`, `/solana`, `/public/*`, `/coingecko/*`)."""
  ws_url: str
  """WebSocket URL."""
  code: NetworkCode
  """Network code signed into every envelope (`n`)."""


MAINNET = NetworkProfile(
  api_url='https://api.margin.trade', ws_url='wss://api.margin.trade/ws', code='m'
)
"""The production deployment (real funds)."""
TESTNET = NetworkProfile(
  api_url='https://testnet-api.margin.trade',
  ws_url='wss://testnet-api.margin.trade/ws',
  code='t',
)
"""The test deployment (faucet funds, `user.faucet_claim`)."""


def network_profile(mainnet: bool) -> NetworkProfile:
  """The deployment to talk to: `MAINNET` when `mainnet`, else `TESTNET`."""
  return MAINNET if mainnet else TESTNET
