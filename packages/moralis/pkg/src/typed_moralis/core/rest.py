"""Moralis's five REST cores, one per real host this client calls: `DeepIndexEndpoint`
(EVM, Bitcoin, Universal, and the deep-index-hosted corner of Solana), `SolanaEndpoint`
(the Solana Gateway), `AuthEndpoint`, `CortexEndpoint`, and `StreamsEndpoint`.

Every one of these hosts shares the same wire shape (an `X-API-Key` header, bare-JSON
request/response, no envelope to unwrap) and differs only in its base URL: each product
resolves to exactly one of the five hosts, baked in via which core class its own endpoints
compose into. Four endpoints that live alongside the rest of Solana's product surface are
actually deep-index-hosted rather than Solana-gateway-hosted like their neighbors: three
(`token_analytics`/`token_analytics_batch`/`token_analytics_timeseries`) sit together in
their own already-homogeneous group, which resolves its own host independently of the
surrounding default; the fourth (`token_search`) sits on its own, not grouped alongside
`token_metadata`/`token_metadata_batch`'s different host -- see `core/base.py`'s module
docstring for why that separation matters. This mirrors alchemy's `core.rest`/`core.rpc`
pattern: a host is a per-subtree fact resolved by which core class an endpoint composes
into, not a per-call argument threaded through every generated call site.
"""

from dataclasses import dataclass
from types import UnionType
import json
import re

from typing_extensions import Any, TypeVar

from typed_core.validation import validator

from .base import MoralisTransport
from .envelope import unwrap_rest

T = TypeVar('T')

MORALIS_USER_AGENT = (
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
  '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
)

API_KEY_HEADER = 'X-API-Key'
"""Credential header name -- constant across every endpoint this client implements
(confirmed: exactly one distinct value across all 178 specs). Backed by `MORALIS_API_KEY`
(`core.auth.env_api_key`), resolved once at `ClientBase.new()`, not per call."""

DEEP_INDEX_URL = 'https://deep-index.moralis.io/api/v2.2'
"""EVM Data API, Bitcoin Data API, Universal API, and the four deep-index-hosted Solana
endpoints (`market_metrics/`'s nested `core` override plus `token_search`'s own direct
leaf position, both described above)."""
SOLANA_URL = 'https://solana-gateway.moralis.io'
"""Solana Data API -- every `solana/` endpoint except the four deep-index-hosted ones."""
AUTH_URL = 'https://authapi.moralis.io'
"""Auth API -- Web3 wallet-signature authentication."""
CORTEX_URL = 'https://cortex-api.moralis.io'
"""Cortex API -- the LLM-backed chat endpoint."""
STREAMS_URL = 'https://api.moralis-streams.com'
"""Streams API -- webhook stream management."""

PATH_PLACEHOLDER = re.compile(r'\{([^{}]+)\}')
"""A `{name}` template slot inside `path` -- design §7's location-marker elimination: a
`request` property matching one is a path parameter, derived from the template itself,
never a declared `path: true` flag. Codegen never excludes a path-matched property from
`request`'s own fields (`native_balance`'s `Request(network=network, address=address)`
carries both, even though `/account/{network}/{address}/balance` templates both), so
substitution and exclusion from the query string/body both happen here, not in generated
code -- the one canonical rule lives in `typed_dev.spec.request.PLACEHOLDER`
(`common/lib`, shared by codegen and the mock server for the same purpose), reproduced
here rather than imported since `core/` is the published package and `typed_dev` is
private repo tooling, never a runtime dependency of it.
"""


@dataclass(kw_only=True, frozen=True)
class RestEndpoint:
  """Shared REST call mechanics (design §2's single `request()` verb) -- every subclass
  supplies only its own resolved base URL, via `_base_url`.
  """

  client: MoralisTransport

  def _base_url(self) -> str:
    """This endpoint's own fixed host."""
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
    """Perform one Moralis REST call: serialize `request` through `request_type`'s
    validator (ADR 0020/S28), route it to the query string for a GET or the JSON body
    for anything else, and validate the reply through `response_type`'s validator.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire path, relative to `_base_url()`.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    values = (
      json.loads(validator(request_type).dump(request))  # type: ignore[arg-type]
      if request_type is not None and request is not None
      else None
    )
    path_params = set(PATH_PLACEHOLDER.findall(path))
    if path_params:
      resolved_path = path.format(**{name: values[name] for name in path_params})  # type: ignore[index]
      values = {k: v for k, v in (values or {}).items() if k not in path_params} or None
    else:
      resolved_path = path
    response = await self.client.http.request(
      method,
      (self.client.base_url or self._base_url()) + resolved_path,
      params=values if method == 'GET' else None,
      json=values if method != 'GET' else None,
      headers={
        'accept': 'application/json',
        'User-Agent': MORALIS_USER_AGENT,
        API_KEY_HEADER: self.client.api_key,
      },
    )
    payload = unwrap_rest(response)
    if response_type is None:
      return None  # type: ignore[return-value]
    if not self.client.should_validate(validate):
      return payload  # type: ignore[return-value]
    return validator(response_type).python(payload)  # type: ignore[arg-type]


@dataclass(kw_only=True, frozen=True)
class DeepIndexEndpoint(RestEndpoint):
  """EVM Data API, Bitcoin Data API, Universal API -- and the four endpoints physically
  under `solana/` that are actually deep-index-hosted (`market_metrics/`'s nested `core`
  override plus `token_search`'s own direct leaf position -- see `core/base.py`'s module
  docstring)."""

  def _base_url(self) -> str:
    return DEEP_INDEX_URL


@dataclass(kw_only=True, frozen=True)
class SolanaEndpoint(RestEndpoint):
  """Solana Data API -- the Solana Gateway host."""

  def _base_url(self) -> str:
    return SOLANA_URL


@dataclass(kw_only=True, frozen=True)
class AuthEndpoint(RestEndpoint):
  """Auth API -- Web3 wallet-signature authentication."""

  def _base_url(self) -> str:
    return AUTH_URL


@dataclass(kw_only=True, frozen=True)
class CortexEndpoint(RestEndpoint):
  """Cortex API -- the LLM-backed chat endpoint."""

  def _base_url(self) -> str:
    return CORTEX_URL


@dataclass(kw_only=True, frozen=True)
class StreamsEndpoint(RestEndpoint):
  """Streams API -- webhook stream management."""

  def _base_url(self) -> str:
    return STREAMS_URL
