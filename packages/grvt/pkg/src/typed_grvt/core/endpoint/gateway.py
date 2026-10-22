"""Base endpoint for GRVT's two gateways (market data and trading).

Both gateways serve the same shape: every RPC is reachable over HTTP and as JSON-RPC over
the gateway's WebSocket, and streams live on that same WebSocket. So one endpoint base
provides both call verbs, `request` and `subscribe`, against one `GatewayClient`.
"""

from dataclasses import dataclass
from types import UnionType

from typing_extensions import Any, Literal, Protocol, Self, TypedDict, TypeVar

from typed_core.util import StreamManager

from ..envelope import Unwrap

T = TypeVar('T')
R = TypeVar('R', default=Any)

Transport = Literal['http', 'ws']
"""Physical transport one RPC is sent over."""

Sign = Literal[
  'order',
  'orders',
  'transfer',
  'withdrawal',
  'derisk',
  'position_config',
  'position_margin',
]
"""Which EIP-712 payload of a request the core signs before sending it:

- `order`: `request["order"]` (`create_order`).
- `orders`: every entry of `request["orders"]` (`bulk_orders`).
- `transfer`, `withdrawal`, `derisk`, `position_config` (`set_position_config`),
  `position_margin` (`add_position_margin`): the request itself.
"""

SubAccount = Literal['request', 'order', 'orders']
"""Where a request carries the `sub_account_id` the core fills in when the caller left it
out (missing or `None`), from the default trading sub-account
(`GatewayTransport.sub_account_id()`):

- `request`: `request["sub_account_id"]` (most trading RPCs, private stream selectors).
- `order`: `request["order"]["sub_account_id"]` (`create_order`).
- `orders`: `request["sub_account_id"]` and each of `request["orders"][i]["sub_account_id"]`
  (`bulk_orders`, which requires the top-level one too).

An explicit value always wins. Filled before signing, so a signature covers it.
"""


class Meta(TypedDict, total=False):
  """Per-endpoint facts the gateway transport needs: how to unwrap the reply, which payload
  to sign, and where to fill the default trading sub-account."""

  unwrap: Unwrap
  """How much of the body to return; `result` when omitted."""
  sign: Sign
  """Payload to sign before sending; nothing is signed when omitted. Only a payload with
  no `signature` (or one without `r`) is signed, so a pre-signed payload goes out as-is."""
  sub_account: SubAccount
  """Where to fill a missing `sub_account_id` from the default trading sub-account; nothing
  is filled when omitted."""


class GatewayClient(Protocol):
  """Structural interface of a gateway transport (`transport.gateway.GatewayTransport`)."""

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    meta: Meta | None = None,
    validate: bool | None = None,
    transport: Transport = 'http',
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Call one RPC over HTTP or the gateway WebSocket and return its unwrapped, validated
    body; see `GatewayEndpoint.request`."""
    ...

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    meta: Meta | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
    reply_type: type[R] | UnionType | None = None,
  ) -> StreamManager[T, R, Any]:
    """Subscribe one `{stream}:{selector}` channel; see `GatewayEndpoint.subscribe`."""
    ...

  async def __aenter__(self) -> Self:
    """Take one (shared) ownership of the transport's connections."""
    ...

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release that ownership; the last owner's exit closes the connections."""
    ...


@dataclass(kw_only=True, frozen=True)
class GatewayEndpoint:
  """Base of every market-data and trading endpoint, and of the routers composing them."""

  client: GatewayClient

  async def __aenter__(self) -> Self:
    """Take one (shared) ownership of the underlying connections; each opens lazily on
    first use."""
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release that ownership; the connections close when their last owner leaves, so a
    block nested in another (or in `async with client`) closes nothing the outer one
    holds."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    meta: Meta | None = None,
    validate: bool | None = None,
    transport: Transport = 'http',
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Call one RPC.

    Args:
      request: The request value (a `TypedDict`), or `None` for an empty request.
      method: HTTP method; `POST` for every gateway RPC, `GET` for `/time`.
      path: HTTP path, e.g. `/full/v1/instrument`. Over WebSocket the JSON-RPC method is
        the path without its `/full/` prefix (`v1/instrument`).
      meta: Per-endpoint facts: envelope handling, payload signing, default sub-account.
      validate: Per-call override of response validation.
      transport: Send over HTTP, or as JSON-RPC over the gateway's WebSocket.
      request_type: Type of `request`, used to serialize it.
      response_type: Type of the returned value, used to validate it.
    """
    return await self.client.request(
      request,
      method=method,
      path=path,
      meta=meta,
      validate=validate,
      transport=transport,
      request_type=request_type,
      response_type=response_type,
    )

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    meta: Meta | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
    reply_type: type[R] | UnionType | None = None,
  ) -> StreamManager[T, R, Any]:
    """Subscribe to one stream selector.

    Args:
      channel: `{stream}:{selector}` template, e.g. `v1.mini.s:{instrument}@{rate}`.
        `{name}` placeholders are filled from `parameters`; a `[...]` group is kept only
        when every placeholder inside it has a value (`v1.fill:{sub_account_id}[-{instrument}]`).
        Parameters no placeholder consumes are sent as extra subscribe params.
      parameters: The parameters value (a `TypedDict`), or `None`.
      meta: Per-endpoint facts: `sub_account` fills a missing `sub_account_id` selector.
      validate: Per-call override of pushed-payload validation.
      request_type: Type of `parameters`, used to serialize it.
      response_type: Type of each pushed `feed`, used to validate it.
      reply_type: Type of the subscribe acknowledgement, used to validate it.
    """
    return self.client.subscribe(
      channel,
      parameters,
      meta=meta,
      validate=validate,
      request_type=request_type,
      response_type=response_type,
      reply_type=reply_type,
    )
