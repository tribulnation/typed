"""dYdX Chain's CometBFT JSON-RPC-over-HTTP transport (design §2/§5/§6, 2026-08-31 codegen
mechanization). `CometClient` is the shared transport every Comet leaf's resolved core
(`CometEndpoint`) forwards through -- host selection (which public dYdX RPC provider) is
a `ChainBase`-level concern (`typed_dydx.chain.core`), not something a Comet leaf or its
resolved core ever chooses for itself.
"""

import json
from dataclasses import dataclass, field
from typing_extensions import Any, NotRequired, Self, TypedDict, TypeVar, cast
from types import UnionType

import httpx
from typed_core.exceptions import ApiError, BadRequest, RateLimited
from typed_core.http import HttpClient
from typed_core.validation import validator

ResultT = TypeVar('ResultT')

DYDX_COMET_OEGS_RPC_URL = 'https://oegs.dydx.trade'
DYDX_COMET_POLKACHU_RPC_URL = 'https://dydx-dao-rpc.polkachu.com'
DYDX_COMET_KINGNODES_RPC_URL = 'https://dydx-ops-rpc.kingnodes.com'
DYDX_COMET_ENIGMA_RPC_URL = 'https://dydx-dao-rpc.enigma-validator.com'
DYDX_COMET_POLKACHU_ARCHIVE_RPC_URL = 'https://dydx-dao-archive-rpc.polkachu.com'
DYDX_COMET_KINGNODES_ARCHIVE_RPC_URL = 'https://dydx-ops-archive-rpc.kingnodes.com'
DYDX_COMET_ENIGMA_ARCHIVE_RPC_URL = 'https://dydx-dao-rpc-archive.enigma-validator.com'

DYDX_COMET_PUBLICNODE_RPC_URL = 'https://dydx-rpc.publicnode.com'
DYDX_COMET_LAVENDERFIVE_RPC_URL = 'https://rpc.lavenderfive.com/dydx'
DYDX_COMET_IMPERATOR_RPC_URL = 'https://rpc-dydx.imperator.co'
DYDX_COMET_RPC_URLS = (
  DYDX_COMET_OEGS_RPC_URL,
  DYDX_COMET_POLKACHU_RPC_URL,
  DYDX_COMET_KINGNODES_RPC_URL,
  DYDX_COMET_ENIGMA_RPC_URL,
)
DYDX_COMET_ARCHIVE_RPC_URLS = (
  DYDX_COMET_POLKACHU_ARCHIVE_RPC_URL,
  DYDX_COMET_KINGNODES_ARCHIVE_RPC_URL,
  DYDX_COMET_ENIGMA_ARCHIVE_RPC_URL,
)
DYDX_COMET_COMMUNITY_RPC_URLS = (
  DYDX_COMET_PUBLICNODE_RPC_URL,
  DYDX_COMET_LAVENDERFIVE_RPC_URL,
  DYDX_COMET_IMPERATOR_RPC_URL,
)
DYDX_COMET_RPC_URL = DYDX_COMET_OEGS_RPC_URL

DYDX_TESTNET_COMET_OEGS_RPC_URL = 'https://oegs-testnet.dydx.exchange'
DYDX_TESTNET_COMET_ENIGMA_RPC_URL = 'https://dydx-rpc-testnet.enigma-validator.com'
DYDX_TESTNET_COMET_KINGNODES_RPC_URL = 'https://test-dydx-rpc.kingnodes.com'
DYDX_TESTNET_COMET_POLKACHU_RPC_URL = 'https://dydx-testnet-rpc.polkachu.com'
DYDX_TESTNET_COMET_RPC_URLS = (
  DYDX_TESTNET_COMET_OEGS_RPC_URL,
  DYDX_TESTNET_COMET_ENIGMA_RPC_URL,
  DYDX_TESTNET_COMET_KINGNODES_RPC_URL,
  DYDX_TESTNET_COMET_POLKACHU_RPC_URL,
)
DYDX_TESTNET_COMET_RPC_URL = DYDX_TESTNET_COMET_OEGS_RPC_URL


class CometOptions(TypedDict, total=False):
  """Options shared by Comet transport constructors."""

  http: HttpClient
  """HTTP transport shared by Comet endpoint calls."""
  validate: bool
  """Default response validation setting."""


class Meta(TypedDict):
  """`comet`'s own `meta` shape (`codegen/config.toml` `[cores.comet].meta`): which query
  parameters (if any) CometBFT only accepts JSON-string-quoted. Hand-written to match
  that declared JSON Schema -- never code-generated (design §2/§6, S27's own precedent)."""

  json_string_params: NotRequired[list[str]]
  """Query parameter names whose value must be sent JSON-string-quoted (`tx_search`'s
  `query`/`order_by`, confirmed live -- an unquoted value returned an invalid-params
  error). Absent/empty for every other Comet endpoint."""


@dataclass(kw_only=True, frozen=True)
class CometClient:
  """Shared CometBFT HTTP transport: one base URL, one underlying HTTP client."""

  base_url: str = DYDX_COMET_RPC_URL
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  async def __aenter__(self) -> Self:
    """Open the shared HTTP transport."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the shared HTTP transport."""
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def close(self):
    """Close the shared HTTP transport."""
    await self.http.__aexit__(None, None, None)

  async def request(self, path: str, *, params: dict[str, Any] | None = None) -> httpx.Response:
    """Send a Comet JSON-RPC-over-HTTP GET request."""
    return await self.http.request('GET', self.base_url + path, params=params)


def raise_http_error(response: httpx.Response):
  """Raise a typed-core exception for a non-OK Comet HTTP response."""
  try:
    payload = response.json()
  except Exception:
    payload = response.text
  raise_api_error(response.status_code, payload)


def raise_api_error(status_code: int, payload: Any):
  """Map a Comet HTTP error to a shared typed-core exception."""
  if status_code == 429:
    raise RateLimited(status_code, payload)
  if 400 <= status_code < 500:
    raise BadRequest(status_code, payload)
  raise ApiError(status_code, payload)


def raise_rpc_error(payload: Any):
  """Map a Comet JSON-RPC error envelope to a shared typed-core exception."""
  code = payload.get('code') if isinstance(payload, dict) else None
  if code == 429 or 'rate' in str(payload).lower():
    raise RateLimited(429, payload)
  if code in {-32700, -32600, -32601, -32602}:
    raise BadRequest(400, payload)
  raise ApiError(200, payload)


@dataclass(kw_only=True, frozen=True)
class CometEndpoint:
  """Base for every generated Comet HTTP endpoint module -- the resolved `core` for the
  `chain/comet/` subtree (`codegen/config.toml`)."""

  client: CometClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[ResultT] | UnionType | None = None,
  ) -> ResultT:
    """Perform one Comet JSON-RPC-over-HTTP GET call (design §2): serialize `request`
    through `request_type`'s validator into a plain query-parameter dict -- JSON-string-
    quoting whichever fields `meta['json_string_params']` names -- unwrap the JSON-RPC
    `result` envelope, and validate it through `response_type`'s validator.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Unused -- every Comet operation is a GET; kept so every generated call can
        pass it uniformly (design §2).
      path: Wire path, e.g. `/block`.
      meta: This call's own quirks -- `json_string_params` (`Meta`'s own docstring).
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    values: dict[str, Any] = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else {}
    )
    for name in meta.get('json_string_params', ()):
      if name in values:
        values[name] = json.dumps(values[name])
    response = await self.client.request(path, params=values or None)
    if response.status_code != 200:
      raise_http_error(response)
    payload = response.json()
    if isinstance(payload, dict) and 'error' in payload:
      raise_rpc_error(payload['error'])
    if not isinstance(payload, dict) or 'result' not in payload:
      raise ApiError(response.status_code, payload)
    result = payload['result']
    should_validate = self.client.validate if validate is None else validate
    if should_validate and response_type is not None:
      return validator(cast(type, response_type)).python(result)
    return cast('ResultT', result)
