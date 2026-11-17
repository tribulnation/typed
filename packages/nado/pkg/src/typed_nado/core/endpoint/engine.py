"""Base endpoint class for the engine APIs: gateway queries, edge queries and executes, and
the trigger service. One `request()` call per endpoint method."""

from typing_extensions import (
  Any,
  Literal,
  NotRequired,
  Protocol,
  Self,
  TypedDict,
  TypeVar,
)
from dataclasses import dataclass
from types import UnionType

from typed_core.validation import validator

from ..signing import SignKind
from .wire import SubaccountField, dump_request

T = TypeVar('T')

Kind = Literal['query', 'edge', 'execute']
"""Which engine door a call goes through:

- `query`: `POST /query` with `{"type": <name>, ...}` (or the same JSON over the socket).
- `edge`: `POST /edge/query`, same body; cached, eventually consistent reads.
- `execute`: `POST /execute` with `{<name>: {...}}` (or the same JSON over the socket).
"""

Transport = Literal['http', 'ws']
"""Gateway calls go over REST or the gateway WebSocket (v1), with identical payloads."""


class EngineMeta(TypedDict):
  """Per-endpoint quirks of an engine call."""

  kind: Kind
  """Which door the call goes through (`Kind`)."""
  sign: NotRequired[SignKind]
  """How the core fills and signs the body before sending it (`core.signing.SignKind`);
  absent for an unsigned call."""
  envelope: NotRequired[Literal['frame']]
  """`frame` for a call whose success carries no `data` (edge `ping`/`time`): return the
  whole success frame instead."""
  default_subaccount: NotRequired[SubaccountField]
  """Fill this request field (`subaccount` or `sender`) with the client's own subaccount
  when the caller leaves it out."""


class EngineClient(Protocol):
  """Structural interface the engine transport implements to back an `EngineEndpoint`."""

  async def call(
    self,
    name: str,
    values: dict[str, Any],
    *,
    kind: Kind,
    sign: SignKind | None = None,
    frame: bool = False,
    default_subaccount: SubaccountField | None = None,
    transport: Transport = 'http',
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one engine call, unwrap its envelope and map errors, then validate.

    Args:
      name: The query `type` or execute name (`status`, `place_order`).
      values: The call's wire values.
      kind: Which door the call goes through.
      sign: Fill and sign `values` this way first.
      frame: Return the whole success frame instead of `data`.
      default_subaccount: Default this field of `values` to the client's subaccount.
      transport: Send over REST or the gateway WebSocket.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    ...


@dataclass(kw_only=True, frozen=True)
class EngineEndpoint:
  """Base class for gateway and trigger endpoints."""

  client: EngineClient
  """The gateway or trigger transport."""

  async def __aenter__(self) -> Self:
    """Return this surface. Nothing opens: transports connect lazily, on first use."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: transports are shared by sibling surfaces, and only the root client
    (`core.base.ClientBase`) closes them."""

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    meta: EngineMeta,
    validate: bool | None = None,
    transport: Transport = 'http',
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one engine call.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: Ignored: every engine call is a JSON `POST` (or a socket frame).
      path: The query `type` or execute name.
      meta: This call's door, signing and envelope quirks.
      validate: Per-call override of response validation.
      transport: Send over REST or the gateway WebSocket.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return await self.client.call(
      path,
      values,
      kind=meta['kind'],
      sign=meta.get('sign'),
      frame=meta.get('envelope') == 'frame',
      default_subaccount=meta.get('default_subaccount'),
      transport=transport,
      validator=response_validator,
      validate=validate,
    )
