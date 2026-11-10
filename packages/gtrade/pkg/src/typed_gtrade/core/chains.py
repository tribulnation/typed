"""The chains gTrade is deployed on, and what each deployment pins: the chain id and
Diamond the Trading API signs for, and the hosts of the chain-scoped services."""

from typing_extensions import Literal, TypeAliasType
from dataclasses import dataclass

Chain = TypeAliasType(
  'Chain', Literal['arbitrum', 'base', 'polygon', 'megaeth', 'arbitrum-sepolia']
)
"""A gTrade deployment, named as in the Trading API's `{chain}` path segment."""

MAINNET_API_URL = 'https://api.gains.trade'
TESTNET_API_URL = 'https://api-testnet.gains.trade'
BACKEND_GLOBAL_URL = 'https://backend-global.gains.trade'
PRICING_URL = 'https://backend-pricing.eu.gains.trade'
PRICING_WS_URL = 'wss://backend-pricing.eu.gains.trade/v3'

REQUEST_DOMAIN_NAME = 'Gains Trading API'
REQUEST_DOMAIN_VERSION = '1'


def ws_url(url: str) -> str:
  """The WebSocket counterpart of an `https://` (or `http://`) URL on the same host."""
  if url.startswith('https://'):
    return 'wss://' + url.removeprefix('https://')
  if url.startswith('http://'):
    return 'ws://' + url.removeprefix('http://')
  return url


@dataclass(frozen=True, kw_only=True)
class Deployment:
  """One chain's deployment: the signing domain and the chain-scoped hosts."""

  chain: Chain
  chain_id: int
  """EVM chain id, the EIP-712 domain `chainId` of Trading API signatures."""
  diamond: str
  """`GNSMultiCollatDiamond`, the EIP-712 `verifyingContract` of Trading API signatures."""
  api_url: str
  """Trading API host root, serving `/health`, `/ready` and `/v1/{chain}/...`."""
  backend_url: str
  """Per-chain trading backend host root; its event stream is the same host over WSS."""

  @property
  def trading_url(self) -> str:
    """Trading API chain root, `{api_url}/v1/{chain}`: every chain-scoped path is relative to it."""
    return f'{self.api_url}/v1/{self.chain}'

  @property
  def trading_ws_url(self) -> str:
    """Trading API WebSocket, `wss://.../v1/{chain}/ws`: one connection serves one chain."""
    return ws_url(self.trading_url) + '/ws'

  @property
  def backend_ws_url(self) -> str:
    """Per-chain backend event stream, served on the bare host root."""
    return ws_url(self.backend_url)


DEPLOYMENTS: dict[Chain, Deployment] = {
  'arbitrum': Deployment(
    chain='arbitrum',
    chain_id=42161,
    diamond='0xFF162c694eAA571f685030649814282eA457f169',
    api_url=MAINNET_API_URL,
    backend_url='https://backend-arbitrum.gains.trade',
  ),
  'base': Deployment(
    chain='base',
    chain_id=8453,
    diamond='0x6cD5aC19a07518A8092eEFfDA4f1174C72704eeb',
    api_url=MAINNET_API_URL,
    backend_url='https://backend-base.gains.trade',
  ),
  'polygon': Deployment(
    chain='polygon',
    chain_id=137,
    diamond='0x209A9A01980377916851af2cA075C2b170452018',
    api_url=MAINNET_API_URL,
    backend_url='https://backend-polygon.gains.trade',
  ),
  'megaeth': Deployment(
    chain='megaeth',
    chain_id=4326,
    diamond='0x2D5B1ba6E2093a5b927Fe5bF8C049B107de31eaF',
    api_url=MAINNET_API_URL,
    backend_url='https://backend-megaeth.gains.trade',
  ),
  'arbitrum-sepolia': Deployment(
    chain='arbitrum-sepolia',
    chain_id=421614,
    diamond='0xd659a15812064C79E189fd950A189b15c75d3186',
    api_url=TESTNET_API_URL,
    backend_url='https://backend-sepolia.gains.trade',
  ),
}
"""Chain ids and Diamonds as the official TypeScript SDK pins them (`CHAINS`), hosts as
the venue publishes them. The Trading API serves only `arbitrum` today; the other
mainnets answer `404 CHAIN_NOT_FOUND` until they launch, and the testnet host is down.

References:
  - [Contract addresses](https://docs.gains.trade/what-is-gains-network/contract-addresses)
"""


def deployment_of(chain: Chain) -> Deployment:
  """The deployment `chain` names.

  Raises:
    ValueError: `chain` is not a known deployment.
  """
  deployment = DEPLOYMENTS.get(chain)
  if deployment is None:
    raise ValueError(
      f'Unknown chain {chain!r}: one of {", ".join(map(repr, DEPLOYMENTS))}'
    )
  return deployment
