"""Shared Comet HTTP transport for dYdX Chain."""

from dataclasses import dataclass, field

import httpx
from pydantic import TypeAdapter
from typed_core.exceptions import ApiError, BadRequest, RateLimited
from typed_core.http import HttpClient
from typing_extensions import Any, Generic, Literal, NotRequired, TypeVar, TypedDict


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

ResultT = TypeVar('ResultT')


class CometError(TypedDict, total=False):
  """JSON-RPC error returned by a Comet endpoint."""

  code: int
  """JSON-RPC error code."""
  message: str
  """Error message."""
  data: NotRequired[Any]
  """Optional error details."""


class CometRpcEnvelope(TypedDict, Generic[ResultT]):
  """JSON-RPC response envelope returned by Comet HTTP endpoints."""

  jsonrpc: Literal['2.0']
  """JSON-RPC protocol version."""
  id: int | str | None
  """Request identifier echoed by the server."""
  result: ResultT
  """Successful method result."""


class CometRpcErrorEnvelope(TypedDict):
  """JSON-RPC error envelope returned by Comet HTTP endpoints."""

  jsonrpc: Literal['2.0']
  """JSON-RPC protocol version."""
  id: int | str | None
  """Request identifier echoed by the server."""
  error: CometError
  """Error returned by the Comet endpoint."""


class CometOptions(TypedDict, total=False):
  """Options shared by Comet endpoint constructors."""

  http: HttpClient
  """HTTP transport shared by Comet endpoint calls."""
  validate: bool
  """Default response validation setting."""


@dataclass(kw_only=True)
class CometEndpoint:
  """Base endpoint with shared Comet HTTP transport."""

  base_url: str = DYDX_COMET_RPC_URL
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  def should_validate(self, validate: bool | None = None) -> bool:
    """Resolve a per-call validation override against the client default."""
    return self.validate if validate is None else validate

  async def __aenter__(self):
    """Open the shared HTTP transport."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the shared HTTP transport."""
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def close(self):
    """Close the shared HTTP transport."""
    await self.http.__aexit__(None, None, None)

  async def request(
    self,
    path: str,
    *,
    params: dict[str, Any] | None = None,
  ) -> httpx.Response:
    """Send a Comet HTTP GET request."""
    return await self.http.request('GET', self.base_url + path, params=params)

  async def result(
    self,
    path: str,
    *,
    result_adapter: TypeAdapter[ResultT],
    params: dict[str, Any] | None = None,
    validate: bool | None = None,
  ) -> ResultT:
    """Return the successful JSON-RPC result or raise a typed-core error."""
    response = await self.request(path, params=params)
    if response.status_code != 200:
      self.raise_http_error(response)
    payload = response.json()
    if isinstance(payload, dict) and 'error' in payload:
      self.raise_rpc_error(payload['error'])
    if not isinstance(payload, dict) or 'result' not in payload:
      raise ApiError(response.status_code, payload)
    result = payload['result']
    if self.should_validate(validate):
      return result_adapter.validate_python(result)
    return result

  def raise_http_error(self, response: httpx.Response):
    """Raise a typed-core exception for non-OK HTTP responses."""
    try:
      payload = response.json()
    except Exception:
      payload = response.text
    self.raise_api_error(response.status_code, payload)

  def raise_api_error(self, status_code: int, payload: Any):
    """Map HTTP errors to shared typed-core exceptions."""
    if status_code == 429:
      raise RateLimited(status_code, payload)
    if 400 <= status_code < 500:
      raise BadRequest(status_code, payload)
    raise ApiError(status_code, payload)

  def raise_rpc_error(self, payload: Any):
    """Map Comet JSON-RPC errors to shared typed-core exceptions."""
    code = payload.get('code') if isinstance(payload, dict) else None
    if code == 429 or 'rate' in str(payload).lower():
      raise RateLimited(429, payload)
    if code in {-32700, -32600, -32601, -32602}:
      raise BadRequest(400, payload)
    raise ApiError(200, payload)


class CometRouter(CometEndpoint):
  """Base class for Comet endpoint groups."""
