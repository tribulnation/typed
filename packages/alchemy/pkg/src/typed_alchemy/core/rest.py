"""REST core classes for Alchemy's plain-REST surfaces (Portfolio, Prices, NFT API v3).

Every one of these products speaks bare REST over the shared `api-key-path` scheme
(`docs/spec/authoring.md` rule 9): confirmed against every real operation this client
specs (`clients/alchemy/spec/endpoints/{nft,portfolio,prices}/**`) that a GET always
carries its fields on the query string and a POST always carries them as a JSON body,
never mixed on one endpoint -- so `RestEndpoint.request()` decides which purely from the
declared HTTP verb, no per-endpoint wire-placement declaration needed (design §2).

`PortfolioEndpoint`/`PricesEndpoint` are zero-arg (one fixed, chain-agnostic host each,
computed from `AlchemyTransport`'s own construction-time override plus the resolved app
API key) -- the degenerate case of design §5a's own forwarding rule, no `.new()` needed.
`ChainNft` is network-parameterized like `core.rpc.ChainRpc`, design §5a's real worked
example applied to a REST surface instead of a JSON-RPC one.
"""

from typing_extensions import Any, Self, TypeVar, cast
from types import UnionType
from dataclasses import dataclass
import json

from typed_core.validation import validator

from .auth import api_key_url
from .base import AlchemyTransport, Network
from .envelope import unwrap_rest

T = TypeVar('T')

ALCHEMY_DATA_API_URL = 'https://api.g.alchemy.com'
"""Shared, chain-agnostic host for Portfolio (`/data/v1`) and Prices (`/prices/v1`)."""

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
"""Per-chain host for NFT API v3."""


def portfolio_url() -> str:
  """Base URL for the Portfolio API (`/data/v1`), without the API key segment."""
  return ALCHEMY_DATA_API_URL + '/data/v1'


def prices_url() -> str:
  """Base URL for the Prices API (`/prices/v1`), without the API key segment."""
  return ALCHEMY_DATA_API_URL + '/prices/v1'


def chain_nft_url(network: Network) -> str:
  """Base URL for NFT API v3 on `network`, without the API key segment."""
  return CHAIN_NFT_HOSTS[network]


@dataclass(kw_only=True, frozen=True)
class RestEndpoint:
  """Shared REST call mechanics (design §2's single `request()` verb) -- every subclass
  supplies only its own resolved base URL, via `_base_url`.
  """

  client: AlchemyTransport

  def _base_url(self) -> str:
    """This endpoint group's own base URL, app API key already baked in."""
    raise NotImplementedError

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one REST call: serialize `request` through `request_type`'s validator
    (ADR 0020/S28), route it to the query string for a GET or the JSON body for anything
    else, and validate the reply through `response_type`'s validator.

    No `meta` parameter: this core declares no `[cores.<name>].meta` schema in
    `codegen/config.toml` (design §2/§6) -- every surface it serves authenticates identically, by
    construction, with no per-call credential or other quirk to decide. Every endpoint
    resolving to this core declares `meta: {}`.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire path, relative to `_base_url()` -- the `{apiKey}` segment never appears
        here; it's already baked into `_base_url()`.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    # `validator(...).dump(...)` returns JSON *bytes* (`typed_core.validation.validator.
    # dump`'s own signature), the right shape for a `content=`-sent POST body but not for
    # `params=`/`json=`, which both need a real dict -- round-tripping through
    # `json.loads` gets one back with every declared format's `PlainSerializer` (S27)
    # already applied, so a GET's query string and a POST's JSON body can share the exact
    # same wire-ready values.
    values = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    response = await self.client.http.request(
      method,
      self._base_url() + path,
      params=values if method == 'GET' else None,
      json=values if method != 'GET' else None,
    )
    payload = unwrap_rest(response)
    if response_type is None:
      return None  # type: ignore[return-value]
    if not self.client.should_validate(validate):
      return payload  # type: ignore[return-value]
    return validator(cast(type, response_type)).python(payload)


@dataclass(kw_only=True, frozen=True)
class PortfolioEndpoint(RestEndpoint):
  """Portfolio APIs: a wallet's onchain holdings across networks -- one fixed,
  chain-agnostic host, no per-call network parameter."""

  def _base_url(self) -> str:
    return self.client.data_base_url or api_key_url(portfolio_url(), self.client.api_key)


@dataclass(kw_only=True, frozen=True)
class PricesEndpoint(RestEndpoint):
  """Prices API: current/historical token prices -- one fixed, chain-agnostic host."""

  def _base_url(self) -> str:
    return self.client.prices_base_url or api_key_url(prices_url(), self.client.api_key)


@dataclass(kw_only=True, frozen=True)
class ChainNft(RestEndpoint):
  """NFT API v3, scoped to one EVM network."""

  base_url: str

  @classmethod
  def new(
    cls, client: AlchemyTransport, *, network: Network | None = None, base_url: str | None = None,
  ) -> Self:
    """Build a chain-scoped NFT core sharing `client`'s already-built transport.

    Args:
      client: Already-built shared transport, forwarded from whichever composing class
        constructs this core.
      network: EVM network every call through this core is scoped to. Defaults to
        `'ethereum'` when omitted.
      base_url: Fully-qualified base URL override, used as-is when given.
    """
    return cls(
      client=client,
      base_url=base_url or api_key_url(chain_nft_url(network or 'ethereum'), client.api_key),
    )

  def _base_url(self) -> str:
    return self.base_url
