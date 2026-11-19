"""Base endpoint class for the request/reply (REST) surfaces.

Every generated REST method is one `RpcEndpoint.request(...)` call: a `Request` value, the
path template, and the endpoint's `meta`. This module decides the wire from those, the same
way for every endpoint:

- a `request` field named by a `{placeholder}` of the path fills it;
- every other field is the query string of a `GET`/`DELETE`, the JSON body otherwise;
- `meta.sign` EIP-712-signs the body as that action. A path field that is also a member of
  the signed struct (`orderId` of a replace, `instrument` of a TP/SL or a position close)
  stays in the body too, since the venue checks the signature against the body;
- `meta.items` names the field whose list is the whole body (the batch endpoints), each
  element signed on its own as `meta.sign`.
"""

from typing_extensions import (
  Any,
  Literal,
  Mapping,
  Protocol,
  Self,
  Sequence,
  TypeVar,
  TypedDict,
  cast,
)
from dataclasses import dataclass
from types import UnionType
from urllib.parse import quote
import json
import re

from typed_core.validation import validator

from ..exc import LogicError
from ..signing import STRUCTS, Action

T = TypeVar('T')

AuthMode = Literal['public', 'optional', 'private']
"""How a request authenticates:

- `public`: never sends credentials.
- `optional`: sends them when the client has some, else goes unauthenticated (demo's
  candle history needs a session; prod's answers anonymously).
- `private`: requires them (`AuthError` on a public client).
"""


class Meta(TypedDict, total=False):
  """Per-endpoint facts of a REST call (`codegen/config.toml`'s `[cores.rpc]`)."""

  auth: AuthMode
  """How the call authenticates; `public` when absent."""
  sign: Action
  """The EIP-712 struct the body is signed as."""
  items: str
  """The `request` field whose list is sent as the whole body, each element signed."""


PLACEHOLDER = re.compile(r'\{([^{}]+)\}')
"""A `{name}` slot of a path template."""

BODYLESS = frozenset({'GET', 'DELETE'})
"""Methods whose non-path fields travel in the query string."""


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    auth: AuthMode = 'public',
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request and return its validated bare payload."""
    ...

  def sign(self, action: Action, body: Mapping[str, Any]) -> dict[str, Any]:
    """EIP-712-sign one body as `action` and return the body to send."""
    ...

  async def __aenter__(self) -> Self:
    """Take ownership of the transport."""
    ...

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release the transport."""
    ...


def wire_value(request: Any, request_type: Any) -> dict[str, Any]:
  """A generated `Request` value in its JSON wire form: timestamps in their wire format,
  decimals as plain strings."""
  if request is None:
    return {}
  if request_type is None:
    return dict(request)
  return json.loads(validator(cast(type, request_type)).dump(request))


def fill_path(template: str, fields: Mapping[str, Any]) -> str:
  """Substitute each `{name}` of `template` with its URL-quoted field.

  Raises:
    LogicError: A placeholder has no field.
  """

  def value(match: re.Match[str]) -> str:
    name = match.group(1)
    if name not in fields:
      raise LogicError(f'Missing path parameter {name!r} for {template!r}')
    return quote(str(fields[name]), safe=':')

  return PLACEHOLDER.sub(value, template)


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for REST endpoints (Exchange, Auth and market-data services)."""

  client: RpcClient

  async def __aenter__(self) -> Self:
    """Enter the transport, for use of this endpoint on its own."""
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Exit the transport."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    meta: Meta = {},
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Send one generated call; see the module docstring for the wire rules.

    Args:
      request: The generated `Request` value, or `None` for a parameterless call.
      method: HTTP method.
      path: Path template, `{name}` placeholders filled from `request`.
      meta: The endpoint's declared quirks.
      validate: Per-call override of response validation.
      request_type: The generated request type, which serializes `request`.
      response_type: The generated response type, which validates the reply.

    Raises:
      AuthError: The call needs credentials (or a wallet key, to sign) the client lacks.
      LogicError: A path parameter is missing.
    """
    fields = wire_value(request, request_type)
    names = set(PLACEHOLDER.findall(path))
    url = fill_path(path, fields)
    rest = {key: value for key, value in fields.items() if key not in names}
    response_validator = (
      validator(cast(type[T], response_type)) if response_type is not None else None
    )
    auth: AuthMode = meta.get('auth', 'public')
    action = meta.get('sign')
    params: Mapping[str, Any] | None = None
    body: Any = None
    if (items := meta.get('items')) is not None:
      elements: Sequence[Mapping[str, Any]] = fields[items]
      body = [
        self.client.sign(action, element) if action is not None else dict(element)
        for element in elements
      ]
    elif action is not None:
      struct = {member['name'] for member in STRUCTS[action]}
      body = self.client.sign(
        action,
        {**rest, **{key: fields[key] for key in names & struct if key in fields}},
      )
    elif method.upper() in BODYLESS:
      params = rest or None
    else:
      body = rest
    return await self.client.request(
      method,
      url,
      params=params,
      json=body,
      auth='private' if action is not None else auth,
      validator=response_validator,
      validate=validate,
    )
