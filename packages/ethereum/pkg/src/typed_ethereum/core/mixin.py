from typing_extensions import Literal
from dataclasses import dataclass
from web3 import AsyncWeb3, PersistentConnectionProvider, AsyncHTTPProvider
from web3.providers import AsyncBaseProvider

Network = Literal[
  'ethereum',
  'bnb-chain',
  'polygon',
  'base',
  'optimism',
  'avalanche',
  'arbitrum',
  'hyperevm',
]

PUBLIC_NODE_URLS: dict[Network, str] = {
  'ethereum': 'https://ethereum-rpc.publicnode.com',
  'bnb-chain': 'https://bsc-rpc.publicnode.com',
  'polygon': 'https://polygon-bor-rpc.publicnode.com',
  'base': 'https://base-rpc.publicnode.com',
  'optimism': 'https://optimism-rpc.publicnode.com',
  'avalanche': 'https://avalanche-c-chain-rpc.publicnode.com',
  'arbitrum': 'https://arbitrum-one-rpc.publicnode.com',
  'hyperevm': 'https://rpc.hyperliquid.xyz/evm',
}

ALCHEMY_NODE_URLS: dict[Network, str] = {
  'ethereum': 'https://eth-mainnet.g.alchemy.com/v2/{API_KEY}',
  'bnb-chain': 'https://bnb-mainnet.g.alchemy.com/v2/{API_KEY}',
  'polygon': 'https://polygon-mainnet.g.alchemy.com/v2/{API_KEY}',
  'base': 'https://base-mainnet.g.alchemy.com/v2/{API_KEY}',
  'optimism': 'https://opt-mainnet.g.alchemy.com/v2/{API_KEY}',
  'avalanche': 'https://avax-mainnet.g.alchemy.com/v2/{API_KEY}',
  'arbitrum': 'https://arb-mainnet.g.alchemy.com/v2/{API_KEY}',
  'hyperevm': 'https://hyperliquid-mainnet.g.alchemy.com/v2/{API_KEY}',
}

@dataclass(kw_only=True)
class NodeRpcMixin:
  """Holds an `AsyncWeb3` node connection and its lifecycle, for any class talking JSON-RPC to a node."""

  w3: AsyncWeb3[AsyncBaseProvider]
  """The node connection. Typed over the common async provider base because this mixin
  handles both an `AsyncHTTPProvider` (built by `at`) and a `PersistentConnectionProvider`
  (entered/exited by `__aenter__`/`__aexit__`). `AsyncWeb3`'s provider parameter is
  invariant, so build your own as `AsyncWeb3[AsyncBaseProvider](provider)` to pass it here."""

  @classmethod
  def at(cls, rpc_url: str, *, poa_middleware: bool = False):
    """Connect over HTTP to `rpc_url`, optionally injecting the POA extra-data middleware."""
    w3 = AsyncWeb3[AsyncBaseProvider](AsyncHTTPProvider(rpc_url))
    if poa_middleware:
      from web3.middleware import ExtraDataToPOAMiddleware
      w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return cls(w3=w3)

  @classmethod
  def public_node(cls, network: Network):
    return cls.at(PUBLIC_NODE_URLS[network])

  @classmethod
  def alchemy(cls, network: Network, api_key: str | None = None):
    import os
    if api_key is None:
      api_key = os.environ['ALCHEMY_API_KEY']
    return cls.at(ALCHEMY_NODE_URLS[network].format(API_KEY=api_key))
  
  async def __aenter__(self):
    if isinstance(self.w3.provider, PersistentConnectionProvider):
      await self.w3.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    if isinstance(self.w3.provider, PersistentConnectionProvider):
      await self.w3.__aexit__(exc_type, exc_value, traceback)
    elif isinstance(self.w3.provider, AsyncHTTPProvider):
      await self.w3.provider.disconnect()
