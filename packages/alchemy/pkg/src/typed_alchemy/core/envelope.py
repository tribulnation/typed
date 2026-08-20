"""Alchemy's two response envelopes and their mapping onto `typed_core` exceptions.

REST endpoints (Portfolio, Prices, NFT v3) return bare JSON with HTTP status as the only
failure discriminator. The enhanced `alchemy_*` methods (Token, Transfers, Utility,
Simulation) ride a standard
JSON-RPC envelope (`{jsonrpc, id, result}` / `{jsonrpc, id, error: {code, message}}`) on
top of that same HTTP layer, so a non-2xx status is still checked first
(`docs/spec/authoring.md` rule 6: alchemy unwraps JSON-RPC and passes its REST half
through under one core).

Alchemy publishes no single JSON-RPC error-code table (`spec/discovery.md`'s Rate
limiting section), so `raise_rpc_error` keeps the same keyword-sniffing heuristic the
client's original core used, ported unchanged rather than guessed anew.
"""

from typing_extensions import Any
import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited


def raise_http_status(response: httpx.Response):
  """Raise the `typed_core` exception matching a non-2xx HTTP status.

  Args:
    response: The unsuccessful HTTP response.

  Raises:
    AuthError: Status `401` or `403`.
    RateLimited: Status `429`.
    BadRequest: Any other `4xx` status.
    ApiError: Any other unsuccessful status.
  """
  try:
    payload: Any = response.json()
  except ValueError:
    payload = response.text
  status = response.status_code
  if status in (401, 403):
    raise AuthError(status, payload)
  if status == 429:
    raise RateLimited(status, payload)
  if 400 <= status < 500:
    raise BadRequest(status, payload)
  raise ApiError(status, payload)


def unwrap_rest(response: httpx.Response) -> Any:
  """Return the parsed JSON body of a bare-REST Alchemy response.

  Args:
    response: The HTTP response to unwrap.

  Raises:
    ApiError: The HTTP status was unsuccessful (via `raise_http_status`).
  """
  if not response.is_success:
    raise_http_status(response)
  return response.json()


def raise_rpc_error(payload: Any):
  """Raise the `typed_core` exception matching a JSON-RPC `error` object.

  Args:
    payload: The JSON-RPC `error` value (usually `{code, message}`, but not guaranteed --
      Alchemy documents no single error shape across all `alchemy_*` methods).

  Raises:
    AuthError: Credential, signature, or permission rejection.
    RateLimited: Request throttled by the venue.
    BadRequest: A standard JSON-RPC parse/invalid-request/method/params error code.
    ApiError: Any other error.
  """
  code = payload.get('code') if isinstance(payload, dict) else None
  text = str(payload).lower()
  if code in (401, 403) or any(
    term in text
    for term in (
      'auth',
      'unauthorized',
      'forbidden',
      'api key',
      'apikey',
      'invalid key',
    )
  ):
    raise AuthError(401, payload)
  if code == 429 or code == -32005 or 'rate' in text:
    raise RateLimited(429, payload)
  if code in (-32700, -32600, -32601, -32602):
    raise BadRequest(400, payload)
  raise ApiError(200, payload)


def unwrap_rpc(response: httpx.Response) -> Any:
  """Return the `result` of a JSON-RPC response.

  Args:
    response: The HTTP response wrapping the JSON-RPC frame.

  Raises:
    ApiError: The HTTP status was unsuccessful, the embedded `error` was set, or neither
      `result` nor `error` was present.
  """
  if not response.is_success:
    raise_http_status(response)
  obj = response.json()
  if 'error' in obj:
    raise_rpc_error(obj['error'])
  if 'result' not in obj:
    raise ApiError(response.status_code, obj)
  return obj['result']
