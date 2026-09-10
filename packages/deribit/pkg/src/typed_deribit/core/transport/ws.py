"""WebSocket transport: Deribit's JSON-RPC 2.0 socket, carrying both RPC method calls
(`RpcClient`) and channel subscriptions (`StreamClient`) on one connection — the same
split `typed_core.ws.StreamsRpc` models directly: `id`-correlated responses vs
`method: "subscription"` pushes carrying no `id`.

Split in two, same shape as `transport/http.py`:

- `SocketConnection` — the wire-level `StreamsRpc`: framing, id correlation, subscription
  routing, heartbeat handling, and enough of its own auth to attach `access_token` to a
  private call. No envelope unwrapping, no response validation.
- `SocketRpcStreamClient` — the `RpcClient`/`StreamClient` Deribit's endpoints actually
  see: unwraps envelopes, validates, and raises `AuthError` for a credential-free client
  before ever touching the wire.

Heartbeat is supported but opt-in (`SocketConnection.heartbeat_interval`, `None` by
default) — matching Deribit's own default of not sending any: enabling it costs an
extra bootstrap RPC on every connect plus a background task per challenge answered,
which a caller who never asked for liveness detection shouldn't pay for. Live testing
against `test.deribit.com` confirmed both the push shape `spec/discovery.md` left
unconfirmed — `{"method": "heartbeat", "params": {"type": "heartbeat" | "test_request"}}`
— and the consequence of enabling it and then ignoring a `test_request`: the server
closes the connection (WS close code `4000`, reason `"heartbeat close"`) within one
interval of the unanswered challenge. A long-lived subscription should pass
`heartbeat_interval=DEFAULT_HEARTBEAT_INTERVAL` (or its own value, `>= 10`) precisely to
detect that kind of silent death instead of hanging forever on a connection Deribit
already gave up on.
"""

from typing_extensions import Any, Mapping, NotRequired, TypeVar, cast
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json
import logging

from typed_core.exceptions import AuthError
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from typed_core.ws import StreamsRpc
from typed_core.ws.streams_rpc import Message, Response, Subscription

from ..auth import AuthResult, Credentials, TokenCache
from ..envelope import unwrap

logger = logging.getLogger(__name__)

T = TypeVar('T')

DERIBIT_WS_URL = 'wss://www.deribit.com/ws/api/v2'
DERIBIT_TEST_WS_URL = 'wss://test.deribit.com/ws/api/v2'

DEFAULT_HEARTBEAT_INTERVAL = 30
"""A reasonable interval for a caller that opts into heartbeat but has no preference of
its own. Deribit documents a 10-second minimum; 30 is comfortably above it without
pushing much traffic. Not used unless `heartbeat_interval` is passed explicitly —
heartbeat itself defaults to off, see module docstring."""


def resolve_ws_url(testnet: bool) -> str:
  """Return Deribit's WebSocket URL for mainnet or testnet."""
  return DERIBIT_TEST_WS_URL if testnet else DERIBIT_WS_URL


class Request(TypedDict):
  """One outgoing JSON-RPC method call, wrapped in the envelope by `rpc_send`."""

  method: str
  params: NotRequired[Mapping[str, Any]]


class Notification(TypedDict):
  """The `params` of a `method: "subscription"` push: `{channel, data}`."""

  channel: str
  data: Any


class SubscriptionParams(TypedDict, total=False):
  """Wire params for a channel subscription.

  `private` isn't a wire field — Deribit takes no extra params on `{public,private}/
  subscribe` beyond the channel list — it's how `SocketConnection.request_subscription`
  picks `private/subscribe` (with `access_token` attached) over `public/subscribe`,
  since `typed_core.ws.Streams`' single `request_subscription` hook has no other way to
  learn that from `subscribe()`/`authed_subscribe()` two levels up.
  """

  private: bool


@dataclass
class SocketConnection(
  StreamsRpc[Request, Any, Notification, SubscriptionParams, list[str], list[str]]
):
  """Deribit's single WebSocket connection: raw JSON-RPC request/reply (any method,
  including the 10 WS-only ones) plus subscription push routing. No envelope unwrapping
  or validation — `SocketRpcStreamClient` layers both on top.
  """

  url: str = DERIBIT_WS_URL
  credentials: Credentials | None = field(default=None, kw_only=True, repr=False)
  heartbeat_interval: int | None = field(default=None, kw_only=True)
  """Seconds between heartbeats, enabled via `public/set_heartbeat` once connected.
  `None` (the default) leaves heartbeat off, matching Deribit's own default. Deribit
  rejects intervals under 10 seconds."""
  tokens: TokenCache | None = field(default=None, init=False, repr=False)
  _background: set[asyncio.Task] = field(default_factory=set, init=False, repr=False)
  """References to fire-and-forget tasks (currently just `test_request` replies), kept
  only so they aren't garbage-collected mid-flight."""

  def __post_init__(self):
    if self.credentials is not None:
      self.tokens = TokenCache(self.credentials)

  async def force_open(self):
    """Connect, then enable heartbeat before returning — so the first caller through
    never races a connection Deribit might otherwise silently drop.

    Bypasses `call`/`rpc_request` for this one bootstrap request and waits with
    `ctx=ctx` directly: `self.wait`'s default (resolving `self.ctx`) would deadlock here,
    since `self.ctx` resolves through this very call, still in progress (see
    `typed_core.ws.Socket.wait`'s docstring).
    """
    ctx = await super().force_open()
    if self.heartbeat_interval is not None:
      id = self.counter
      self.counter += 1
      self.replies[id] = asyncio.Future()
      await ctx.ws.send(
        json.dumps(
          {
            'jsonrpc': '2.0',
            'id': id,
            'method': 'public/set_heartbeat',
            'params': {'interval': self.heartbeat_interval},
          }
        )
      )
      envelope = await self.wait(self.replies[id], ctx=ctx)
      del self.replies[id]
      unwrap(envelope)
    return ctx

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Cancel any `test_request` replies still in flight before closing the connection
    they'd otherwise try to answer on — `Socket.__aexit__`/`StreamsRpc.__aexit__` know
    nothing about `_background`, so left to them these tasks would either send on a
    socket mid-close or get silently garbage-collected pending."""
    tasks = list(self._background)
    for task in tasks:
      task.cancel()
    if tasks:
      await asyncio.gather(*tasks, return_exceptions=True)
    await super().__aexit__(exc_type, exc_value, traceback)

  async def rpc_send(self, id: int, req: Request):
    ws = await self.ws
    await ws.send(json.dumps({'jsonrpc': '2.0', 'id': id, **req}))

  def parse_msg(self, msg: str | bytes) -> Message[Any, Notification] | None:
    obj = json.loads(msg)
    if 'id' in obj:
      return Response(kind='response', id=obj['id'], response=obj)
    elif obj.get('method') == 'subscription':
      params = obj['params']
      return Subscription(
        kind='subscription', channel=params['channel'], notification=params
      )
    elif obj.get('method') == 'heartbeat':
      if obj.get('params', {}).get('type') == 'test_request':
        # Answer inline, not from `self.wait(...)`'s caller: nothing here should block
        # `on_msg`/the listener loop, and there may be no in-flight caller to piggyback
        # the answer on anyway.
        self._spawn(self._answer_test_request())
      return None
    else:
      return None

  def _spawn(self, coro):
    task = asyncio.create_task(coro)
    self._background.add(task)
    task.add_done_callback(self._background.discard)

  async def _answer_test_request(self):
    try:
      await self.call('public/test')
    except Exception:
      logger.warning(
        'Failed to answer Deribit test_request heartbeat challenge', exc_info=True
      )

  async def call(self, method: str, params: Mapping[str, Any] | None = None) -> Any:
    """Send one JSON-RPC method call and return its unwrapped `result`."""
    envelope = await self.rpc_request({'method': method, 'params': params or {}})
    return unwrap(envelope)

  async def authenticate(self, credentials: Credentials) -> AuthResult:
    """Exchange `client_id`/`client_secret` for an access token via `public/auth`."""
    return await self.call(
      'public/auth',
      {
        'grant_type': 'client_credentials',
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
      },
    )

  async def request_subscription(
    self,
    channel: str,
    params: SubscriptionParams | None = None,
  ) -> list[str]:
    """Subscribe to `channel` and return the channels this call actually subscribed to.

    Deribit's `{public,private}/subscribe` reply `result` is always a bare list of
    channel names (confirmed against captured examples and upstream docs), never a
    dict — never `None` either, despite the base class's own `SubscriptionReply`
    default.
    """
    private = (params or {}).get('private', False)
    req_params: dict[str, Any] = {'channels': [channel]}
    if private:
      if self.tokens is None:
        raise AuthError(
          f'Channel "{channel}" requires credentials; build the client with '
          '`Deribit.new(client_id=..., client_secret=...)`.'
        )
      req_params['access_token'] = await self.tokens.get(self.authenticate)
    return await self.call(
      'private/subscribe' if private else 'public/subscribe', req_params
    )

  async def request_unsubscription(
    self,
    channel: str,
    params: SubscriptionParams | None = None,
  ) -> list[str]:
    """Unsubscribe from `channel` and return the channels this call actually
    unsubscribed from.

    Same wire shape as `request_subscription` — see its docstring.
    """
    private = (params or {}).get('private', False)
    req_params: dict[str, Any] = {'channels': [channel]}
    if private and self.tokens is not None:
      req_params['access_token'] = await self.tokens.get(self.authenticate)
    return await self.call(
      'private/unsubscribe' if private else 'public/unsubscribe', req_params
    )


@dataclass(kw_only=True)
class SocketRpcStreamClient:
  """WebSocket RPC and Streams client, owning connection, authentication and validation.

  Implements both `endpoint.rpc.RpcClient` and `endpoint.stream.StreamClient`
  structurally — Deribit's socket genuinely answers both request/reply and
  subscriptions on the one connection, so one object plays both roles rather than
  splitting into two that would have to share `conn` anyway.
  """

  conn: SocketConnection = field(default_factory=SocketConnection)
  validate: bool = True

  @classmethod
  def new(
    cls,
    url: str = DERIBIT_WS_URL,
    *,
    credentials: Credentials | None = None,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    heartbeat_interval: int | None = None,
  ):
    """Build one subtree. Thin: no environment lookup — `Deribit.new()` (`../../main.py`)
    owns that, for both this and the HTTP transport.

    Args:
      heartbeat_interval: Seconds between heartbeats; `None` (default) leaves it off,
        matching Deribit's own default. Pass `DEFAULT_HEARTBEAT_INTERVAL` or your own
        value (`>= 10`) for a long-lived connection that should detect silent death
        instead of hanging on a socket Deribit already dropped.
    """
    conn = SocketConnection(
      url=url,
      credentials=credentials,
      timeout=timeout,
      heartbeat_interval=heartbeat_interval,
    )
    return cls(conn=conn, validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of this client's `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self):
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    result = await self.conn.call(method, params)
    if validator is not None and self.should_validate(validate):
      return validator.python(result)
    return result

  async def authed_request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an `access_token`-authenticated request, lazily exchanging and caching a
    token.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.conn.credentials is None or self.conn.tokens is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    token = await self.conn.tokens.get(self.conn.authenticate)
    result = await self.conn.call(method, {**(params or {}), 'access_token': token})
    if validator is not None and self.should_validate(validate):
      return validator.python(result)
    return result

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    manager = self.conn.subscribe(channel, SubscriptionParams(private=False))
    if validator is None or not self.should_validate(validate):
      return cast('StreamManager[T, Any, Any]', manager)
    return manager.map(lambda n: validator(n['data']))

  def authed_subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    manager = self.conn.subscribe(channel, SubscriptionParams(private=True))
    if validator is None or not self.should_validate(validate):
      return cast('StreamManager[T, Any, Any]', manager)
    return manager.map(lambda n: validator(n['data']))
