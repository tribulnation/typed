"""Engine transport: gateway queries, edge queries and executes (REST or WebSocket v1), and
the trigger service (REST only). Owns the envelope, signing and validation."""

from typing_extensions import Any, TypeVar
from dataclasses import dataclass, field
import asyncio

from typed_core.http import HttpClient
from typed_core.validation import validator

from ..endpoint.engine import EngineClient, Kind, Transport
from ..envelope import decode, unwrap_engine
from ..exc import AuthError, BadRequest, LogicError, ValidationError
from ..endpoint.wire import SubaccountField
from ..signing import SignKind, Signer, with_default_subaccount, needs_tx_nonce, prepare
from .http import post_json
from .ws import GatewaySocket

T = TypeVar('T')

PATHS: dict[Kind, str] = {
  'query': '/query',
  'edge': '/edge/query',
  'execute': '/execute',
}
"""REST path of each engine door, below the gateway or trigger base."""


def wire_frame(name: str, values: dict[str, Any], kind: Kind) -> dict[str, Any]:
  """The JSON a call sends, over REST or the socket alike: `{"type": name, ...}` for a query,
  `{name: {...}}` for an execute."""
  if kind == 'execute':
    return {name: values}
  return {'type': name, **values}


@dataclass(kw_only=True)
class EngineTransport(EngineClient):
  """One engine service (the gateway or the trigger service): its REST base, its socket
  when it has one, and the client's signer."""

  http: HttpClient
  """The client's shared HTTP connection pool."""
  base_url: str
  """REST base the engine paths hang off (`.../gateway/v1`, `.../trigger/v1`)."""
  socket: GatewaySocket | None = None
  """The gateway WebSocket; `None` for the trigger service, which has none."""
  signer: Signer | None = None
  """Signs executes and signed reads; `None` for a public client."""
  validate: bool = True
  """Validate responses by default."""
  tx_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  """Held from fetching a sequential `tx_nonce` until the execute using it is answered, so
  two such executes never sign the same nonce."""

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  def require_signer(self, what: str) -> Signer:
    """The client's signer.

    Raises:
      AuthError: The client was built with `public=True`.
    """
    if self.signer is None:
      raise AuthError(
        f'{what} needs a signing key; this client was built with `public=True`.'
      )
    return self.signer

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
    """Send one engine call; see `EngineClient.call`.

    Raises:
      AuthError: The call is signed, or omits a subaccount it would default to the
        client's own, on a public client; or the venue rejected the signature.
      BadRequest: A signed field is missing or invalid, or the venue refused the request.
      RateLimited: The venue throttled the request.
      ApiError: Any other venue error.
      LogicError: `transport='ws'` on the trigger service.
    """
    values = with_default_subaccount(name, values, default_subaccount, self.signer)
    if sign is None:
      result = await self.send(
        name, values, kind=kind, frame=frame, transport=transport
      )
    else:
      signer = self.require_signer(name)
      if needs_tx_nonce(sign, values):
        async with self.tx_lock:
          body = await prepare(sign, values, signer, self.next_tx_nonce)
          result = await self.send(
            name, body, kind=kind, frame=frame, transport=transport
          )
      else:
        body = await prepare(sign, values, signer, self.next_tx_nonce)
        result = await self.send(
          name, body, kind=kind, frame=frame, transport=transport
        )
    if validator is not None and self.should_validate(validate):
      return validator.python(result)
    return result

  async def next_tx_nonce(self) -> str:
    """The wallet's next sequential `tx_nonce`, from the gateway's `nonces` query.

    Raises:
      ValidationError: The `nonces` reply carries no `tx_nonce`.
    """
    signer = self.require_signer('nonces')
    data = await self.send(
      'nonces', {'address': signer.credentials.owner}, kind='query', transport='http'
    )
    if not isinstance(data, dict) or 'tx_nonce' not in data:
      raise ValidationError(f'Unexpected nonces reply: {data!r:.200}')
    return str(data['tx_nonce'])

  async def send(
    self,
    name: str,
    values: dict[str, Any],
    *,
    kind: Kind,
    frame: bool = False,
    transport: Transport = 'http',
  ) -> Any:
    """Send one ready body and return its unwrapped result (unvalidated)."""
    payload = wire_frame(name, values, kind)
    if transport == 'ws':
      if self.socket is None:
        raise LogicError(f'{name}: this service has no WebSocket transport')
      raw = await self.socket.call(payload)
      decoded = decode(raw)
      if (
        decoded is None
      ):  # a plain-text rejection: the frame did not parse as a request
        raise BadRequest(raw if isinstance(raw, str) else raw.decode(errors='replace'))
      return unwrap_engine(decoded, frame=frame, echo_id=kind == 'execute')
    decoded = await post_json(self.http, self.base_url + PATHS[kind], payload)
    return unwrap_engine(decoded, frame=frame, echo_id=kind == 'execute')
