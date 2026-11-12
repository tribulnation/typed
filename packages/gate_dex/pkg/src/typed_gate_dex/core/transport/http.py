"""The Gate DEX HTTP transport: one signed `POST` per action."""

from typing_extensions import Any, Literal, Mapping, TypeVar, cast
from dataclasses import dataclass, field
from types import UnionType
import json

from typed_core.http import HttpClient
from typed_core.validation import validator

from ..auth import Credentials, auth_headers
from ..endpoint.rpc import Meta, RpcClient
from ..envelope import unwrap
from ..types import timestamp_millis

T = TypeVar('T')

GATE_DEX_API_URL = 'https://openapi.gateweb3.cc'
"""Production host. There is no testnet."""
API_PATH = '/api/v1/dex'
"""The one route every action is posted to. The signature always covers `auth.SIGN_PATH`,
the same literal, whatever URL is actually requested (a mock server's, say)."""


def encode_params(
  request: Mapping[str, Any] | None, request_type: type[Any] | UnionType | None
) -> bytes:
  """Serialize an action's `params` to compact JSON bytes.

  Goes through `validator(request_type).dump`, so timestamp and decimal fields render in
  their wire format. `None` is `{}`: the venue expects `params` on every action.

  Args:
    request: The params to send.
    request_type: The `TypedDict` (or union of them) describing them; a plain `dict`
      when omitted.
  """
  if request is None:
    return b'{}'
  # pydantic adapts a union as readily as a class; `validator` is only typed `type[T]`.
  params_type = cast(type[Any], request_type if request_type is not None else dict)
  return validator(params_type).dump(request)


def encode_body(action: str, params: bytes) -> bytes:
  """Build the request body `{"action":...,"params":...}`, compact, `action` first.

  These exact bytes are both signed and sent, so nothing re-serializes them afterwards.

  Args:
    action: Action name, e.g. `trade.swap.quote`.
    params: Already-serialized params, from `encode_params`.
  """
  return b'{"action":' + json.dumps(action).encode() + b',"params":' + params + b'}'


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """Signed HTTP client owning the connection, the credentials and the validation default."""

  credentials: Credentials
  """Every action is authenticated; there is no public surface."""
  base_url: str = GATE_DEX_API_URL
  """Host every action is posted to, with any trailing `/` dropped and `API_PATH` appended; overridable for a mock."""
  http: HttpClient = field(default_factory=HttpClient)
  """Underlying `typed_core` HTTP client; it opens its connection on the first request."""
  validate: bool = True
  """Client-level default for response validation; each call can override it."""

  async def __aenter__(self):
    """Take ownership of the HTTP client; it connects on the first request."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the HTTP client, if a request opened it."""
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def request(
    self,
    request: Mapping[str, Any] | None = None,
    *,
    method: Literal['POST'] = 'POST',
    path: str,
    meta: Meta | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Sign and send one action, then unwrap and validate its result.

    The body is serialized once; those exact bytes are signed and posted.

    Args:
      request: The action's `params`; `None` sends `{}`.
      method: HTTP verb; the venue only accepts `POST`.
      path: The action name.
      meta: Per-action quirks; `keep_envelope` returns the whole envelope.
      validate: Override response validation for this call.
      request_type: Type `request` is serialized through; may be a union.
      response_type: Type the result is validated against; may be a union.

    Raises:
      NetworkError: The request could not be sent.
      ApiError: The venue rejected it (`AuthError`, `RateLimited`, `BadRequest` where the
        code says so).
      ValidationError: The response did not match `response_type` or the envelope.
    """
    body = encode_body(path, encode_params(request, request_type))
    headers = {
      'Content-Type': 'application/json',
      **auth_headers(self.credentials, timestamp=timestamp_millis.now(), body=body),
    }
    response = await self.http.request(
      method, self.base_url.rstrip('/') + API_PATH, content=body, headers=headers
    )
    keep_envelope = meta is not None and meta.get('keep_envelope', False)
    payload = unwrap(response, keep_envelope=keep_envelope)
    if response_type is not None and self.should_validate(validate):
      return validator(cast(type[T], response_type)).python(payload)
    return payload
