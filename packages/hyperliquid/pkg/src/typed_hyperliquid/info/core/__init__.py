"""Info endpoint base: RPC-shaped, unauthenticated, reachable over HTTP or the shared
WebSocket connection. See `spec/core.md` for the full surface writeup.

Every `info.*` operation posts the same shape to one fixed surface: a flat JSON object
carrying a `type` discriminator plus that action's own fields, with no further wire-
placement decision to make (design §2/§7) -- `path` (`RpcEndpointSpec.path`, e.g.
`"l2Book"`, `"allMids"`) *is* the wire `type` value, the same convention alchemy's own
`ChainRpc.request` reuses `path` for (there, a JSON-RPC method name; here, an action
discriminator), never a URL to route on.
"""

from typing_extensions import Any, Literal, Self, TypeVar, cast
from types import UnionType
from dataclasses import dataclass
from datetime import timedelta

from typed_core.exceptions import ApiError
from typed_core.http import HttpClient
from typed_core.validation import validator

from typed_hyperliquid.core.endpoint.rpc import RpcClient, RpcEndpoint
from typed_hyperliquid.core.urls import http_base_url, ws_url as resolve_ws_url
from typed_hyperliquid.core.wire import dump_request
from typed_hyperliquid.core.ws import SocketClient
from .transport.http import InfoHttpClient
from .transport.ws import InfoSocketClient

T = TypeVar('T')

InfoClient = RpcClient
"""Transport for Hyperliquid info requests -- same shape as the shared `RpcClient`."""

_NULL_MEANS_MISSING: frozenset[str] = frozenset({'l2Book'})
"""`info.*` wire types whose venue response is a bare `null` when the queried resource
doesn't exist, rather than an error -- raised here as `ApiError` instead of returned as
`None`, so a caller isn't silently handed a value typed to never be `None`. `l2Book`'s
`coin` request field names the resource in the raised message."""


@dataclass(kw_only=True)
class InfoCore(RpcEndpoint):
  """Base for Hyperliquid info endpoint groups."""

  ws_client: RpcClient | None = None
  """The alternate transport a per-call `transport='ws'` selects (`request`'s own
  `transport` parameter). Unset on an instance already built WS-only (`.ws`/`.ws_of`) --
  there's nothing to switch to, so every call there must stay on the default
  `transport='http'` (`self.client` itself is the WS-backed transport in that case)."""

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
    transport: Literal['http', 'ws'] = 'http',
  ) -> T:
    """Perform one `info` call: dump `request` through its own validator, place it on the
    wire as `{"type": path, ...fields}`, POST or send it over the requested transport, and
    validate the reply through `response_type`'s validator.

    No `meta` parameter: this core declares no `[cores.<name>].meta` schema in
    `codegen/config.toml` (design §2/§6) -- every `info` call is unauthenticated, with no other
    per-call quirk to decide. Every endpoint resolving to this core declares `meta: {}`.

    Args:
      request: The generated `Request` value, or `None` for a parameterless operation.
      method: Unused -- `info` has exactly one wire operation (`POST /info`), selected by
        the `type` field this method itself injects; kept only so this signature matches
        `ExchangeCore.request`'s.
      path: The wire `type` discriminator, e.g. `"l2Book"`.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
      transport: Which transport carries this call (S23, `docs/production_standards.md`)
        -- `self.client` (`'http'`, the default) or `self.ws_client` (`'ws'`). The `info`
        response is byte-identical either way, so this changes nothing else about how the
        call is built or validated.

    Raises:
      ValueError: `transport='ws'` was requested, but this instance has no WebSocket
        transport configured.
    """
    if transport == 'ws':
      if self.ws_client is None:
        raise ValueError('No WebSocket transport is configured for this Info client.')
      client = self.ws_client
    else:
      client = self.client
    values = dump_request(request, request_type)
    payload = {'type': path, **values}
    result = await client.request(payload)
    if path in _NULL_MEANS_MISSING and result is None:
      raise ApiError(f'L2 book "{values.get("coin")}" not found')
    should_validate = self.validate if validate is None else validate
    if response_type is None:
      return None  # type: ignore[return-value]
    if not should_validate:
      return result
    return validator(cast(type, response_type)).python(result)

  @classmethod
  def new(
    cls, client: RpcClient, *, info_ws_client: RpcClient | None = None, validate: bool = True,
  ) -> Self:
    """Build an Info core forwarding a root client's already-built transports (design
    §5a) -- not meant to be called directly; `client.info`'s generated `@cached_property`
    calls this, forwarding `ClientBase`'s own same-named fields.

    Args:
      client: The active (HTTP-backed, by default) transport.
      info_ws_client: The alternate transport a per-call `transport='ws'` selects.
      validate: Validate responses.
    """
    return cls(client=client, ws_client=info_ws_client, validate=validate)

  @classmethod
  def http(
    cls,
    *,
    mainnet: bool = True,
    validate: bool = True,
    http: HttpClient | None = None,
    ws: SocketClient | None = None,
    base_url: str | None = None,
  ) -> Self:
    """Create an Info client, active over HTTP with an optional WebSocket alternate (a
    per-call `transport='ws'`) available on the same instance (S23).

    Args:
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      http: Shared HTTP transport.
      ws: Shared WebSocket transport, selected by a per-call `transport='ws'`. Omit to
        build an HTTP-only instance -- `transport='ws'` then raises `ValueError`.
      base_url: Custom HTTP API root. If provided, takes precedence over `mainnet`.
    """
    client = InfoHttpClient(
      base_url=base_url or http_base_url(mainnet), http=http or HttpClient()
    )
    ws_client = InfoSocketClient(ws=ws) if ws is not None else None
    return cls(client=client, ws_client=ws_client, validate=validate)

  @classmethod
  def ws_of(cls, ws: SocketClient, *, validate: bool = True) -> Self:
    """Create an Info client from an existing WebSocket transport.

    Args:
      ws: Shared WebSocket transport.
      validate: Validate responses.
    """
    return cls(client=InfoSocketClient(ws=ws), validate=validate)

  @classmethod
  def ws(
    cls,
    *,
    mainnet: bool = True,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    ws_url: str | None = None,
  ) -> Self:
    """Create an Info client with WebSocket transport.

    Args:
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      timeout: WebSocket request timeout.
      ws_url: Custom WebSocket URL. If provided, takes precedence over `mainnet`.
    """
    ws = SocketClient(url=ws_url or resolve_ws_url(mainnet), timeout=timeout)
    return cls.ws_of(ws, validate=validate)


__all__ = ['InfoClient', 'InfoCore', 'InfoHttpClient', 'InfoSocketClient']
