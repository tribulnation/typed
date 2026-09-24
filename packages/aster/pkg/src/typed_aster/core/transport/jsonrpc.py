"""HTTP transport for the Aster Chain JSON-RPC 2.0 endpoint (`POST tapi.asterdex.com/info`).

Replies are `{jsonrpc, id, result}` or `{jsonrpc, id, error: {code, message}}`, always
with HTTP 200. The transport unwraps `result` and raises on `error`.
"""

from typing_extensions import Any, NotRequired, Sequence, TypeVar
from dataclasses import dataclass, field
import json

import httpx

from typed_core.exceptions import ApiError, BadRequest, ValidationError
from typed_core.http import HttpClient
from typed_core.validation import TypedDict, validator

from ..endpoint.jsonrpc import JsonRpcClient
from ..envelope import decode, raise_error

T = TypeVar('T')

ASTER_CHAIN_RPC_URL = 'https://tapi.asterdex.com/info'

BAD_REQUEST_CODES = frozenset({-32700, -32600, -32601, -32602})
"""JSON-RPC parse error, invalid request, method not found, invalid params."""


class RpcError(TypedDict):
  """A JSON-RPC error object."""

  code: int
  message: str
  data: NotRequired[Any]


class Envelope(TypedDict):
  """A JSON-RPC 2.0 reply."""

  jsonrpc: str
  id: Any
  result: NotRequired[Any]
  error: NotRequired[RpcError]


validate_envelope = validator(Envelope)


def unwrap(response: httpx.Response) -> Any:
  """Return the `result` of a JSON-RPC reply.

  Raises:
    BadRequest: A JSON-RPC client error (unknown method, invalid params, ...).
    ApiError: Any other JSON-RPC error, or an unsuccessful HTTP status.
    ValidationError: The body is not a JSON-RPC reply.
  """
  try:
    payload = decode(response.content)
  except ValueError:
    payload = response.text
  if not response.is_success:
    raise_error(response.status_code, payload)
  envelope = validate_envelope.python(payload)
  if (error := envelope.get('error')) is not None:
    if error['code'] in BAD_REQUEST_CODES:
      raise BadRequest(error['code'], error['message'], envelope)
    raise ApiError(error['code'], error['message'], envelope)
  if 'result' not in envelope:
    raise ValidationError(f'JSON-RPC reply without result or error: {envelope}')
  return envelope['result']


@dataclass(kw_only=True)
class HttpJsonRpcClient(JsonRpcClient):
  """JSON-RPC client over HTTP, owning the connection and validation."""

  url: str = ASTER_CHAIN_RPC_URL
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True
  counter: int = field(default=0, init=False, repr=False)

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def call(
    self,
    method: str,
    params: Sequence[Any],
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Call one JSON-RPC method and return its validated `result`."""
    self.counter += 1
    body = {
      'jsonrpc': '2.0',
      'id': self.counter,
      'method': method,
      'params': list(params),
    }
    response = await self.http.request(
      'POST',
      self.url,
      content=json.dumps(body),
      headers={'Content-Type': 'application/json'},
    )
    result = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(result)
    return result
