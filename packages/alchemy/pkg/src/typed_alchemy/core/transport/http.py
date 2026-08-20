"""HTTP transport for Alchemy's `api-key-path` auth scheme.

Every surface this client implements in this pass -- Chain APIs, the enhanced
`alchemy_*` JSON-RPC methods, NFT API v3, Portfolio, Prices -- authenticates the same
way: the app API key is a path segment of the request URL itself
(`ApiKeyPathHttpClient`), resolved once by `auth.resolve_api_key`/`auth.api_key_url` and
baked into `base_url` at construction time. One client class serves both REST verbs
(`request`) and the JSON-RPC `alchemy_*` methods (`rpc`), matching
`docs/spec/authoring.md` rule 6's "alchemy unwraps JSON-RPC and passes its REST half
through under one core" -- the client's original core already did this with one
`Endpoint.request`/`Endpoint.rpc_request` pair, ported here unchanged in shape.
"""

from typing_extensions import Any, Literal, Mapping, TypeVar
from dataclasses import dataclass, field

from typed_core.http import HttpClient
from typed_core.validation import validator

from ..endpoint.rpc import JsonRpcClient
from ..envelope import unwrap_rest, unwrap_rpc

T = TypeVar('T')

ALCHEMY_DATA_API_URL = 'https://api.g.alchemy.com'
"""Shared, chain-agnostic host for Portfolio (`/data/v1`) and Prices (`/prices/v1`)."""

Network = Literal[
  'ethereum',
  'bnb',
  'polygon',
  'base',
  'avalanche',
  'optimism',
  'arbitrum',
  'gnosis',
  'celo',
]
"""EVM chains this client wires a base URL for. Alchemy documents 100+ chains total
(`spec/discovery.md`'s Domains section); this is the pre-existing, already-wired subset,
carried over unchanged from the client's original hand-written core
(`core/mixin.py`)."""

CHAIN_RPC_HOSTS: dict[Network, str] = {
  'ethereum': 'https://eth-mainnet.g.alchemy.com/v2',
  'bnb': 'https://bnb-mainnet.g.alchemy.com/v2',
  'polygon': 'https://polygon-mainnet.g.alchemy.com/v2',
  'base': 'https://base-mainnet.g.alchemy.com/v2',
  'avalanche': 'https://avax-mainnet.g.alchemy.com/v2',
  'optimism': 'https://opt-mainnet.g.alchemy.com/v2',
  'arbitrum': 'https://arb-mainnet.g.alchemy.com/v2',
  'gnosis': 'https://gnosis-mainnet.g.alchemy.com/v2',
  'celo': 'https://celo-mainnet.g.alchemy.com/v2',
}
"""Per-chain host for Chain APIs and the enhanced `alchemy_*` JSON-RPC methods (Token,
Transfers, Utility, Simulation)."""

CHAIN_NFT_HOSTS: dict[Network, str] = {
  'ethereum': 'https://eth-mainnet.g.alchemy.com/nft/v3',
  'bnb': 'https://bnb-mainnet.g.alchemy.com/nft/v3',
  'polygon': 'https://polygon-mainnet.g.alchemy.com/nft/v3',
  'base': 'https://base-mainnet.g.alchemy.com/nft/v3',
  'avalanche': 'https://avax-mainnet.g.alchemy.com/nft/v3',
  'optimism': 'https://opt-mainnet.g.alchemy.com/nft/v3',
  'arbitrum': 'https://arb-mainnet.g.alchemy.com/nft/v3',
  'gnosis': 'https://gnosis-mainnet.g.alchemy.com/nft/v3',
  'celo': 'https://celo-mainnet.g.alchemy.com/nft/v3',
}
"""Per-chain host for NFT API v3, the same chain family as `CHAIN_RPC_HOSTS` on a
`/nft/v3` path instead of `/v2`."""


@dataclass(kw_only=True)
class ApiKeyPathHttpClient(JsonRpcClient):
  """REST + JSON-RPC transport for every `api-key-path`-authenticated surface.

  `base_url` already carries the resolved API key (see `auth.api_key_url`) -- every call
  is authenticated by construction, so there is no unauthenticated variant to expose.
  """

  base_url: str
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send a REST request to `base_url + path`."""
    response = await self.http.request(
      method, self.base_url + path, json=json, params=params
    )
    payload = unwrap_rest(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload

  async def rpc(
    self,
    method: str,
    params: Any | None = None,
    *,
    id: int = 1,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send a JSON-RPC request (an `alchemy_*` enhanced method) to `base_url`.

    Args:
      method: The JSON-RPC method name, e.g. `alchemy_getTokenBalances`.
      params: The wire `params` value. Most enhanced methods take a single object or
        scalar argument, wrapped here in the one-element JSON-RPC `params` array
        (`alchemy_getTokenAllowance`, `alchemy_getTokenMetadata`). A method whose
        positional argument list is itself the JSON-RPC `params` array --
        `alchemy_getTokenBalances`'s `[address, tokenSpec?, options?]`,
        `alchemy_simulateAssetChangesBundle`'s `[tx, ...]` -- passes that list
        directly, sent as-is rather than wrapped again.
      id: JSON-RPC request id.
    """
    if params is None:
      wire_params: list[Any] = []
    elif isinstance(params, list):
      wire_params = params
    else:
      wire_params = [params]
    body: dict[str, Any] = {
      'jsonrpc': '2.0',
      'id': id,
      'method': method,
      'params': wire_params,
    }
    response = await self.http.request('POST', self.base_url, json=body)
    payload = unwrap_rpc(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload


def portfolio_url() -> str:
  """Base URL for the Portfolio API (`/data/v1`), without the API key segment."""
  return ALCHEMY_DATA_API_URL + '/data/v1'


def prices_url() -> str:
  """Base URL for the Prices API (`/prices/v1`), without the API key segment."""
  return ALCHEMY_DATA_API_URL + '/prices/v1'


def chain_rpc_url(network: Network) -> str:
  """Base URL for Chain APIs / enhanced JSON-RPC methods on `network`, without the API
  key segment.
  """
  return CHAIN_RPC_HOSTS[network]


def chain_nft_url(network: Network) -> str:
  """Base URL for NFT API v3 on `network`, without the API key segment."""
  return CHAIN_NFT_HOSTS[network]
