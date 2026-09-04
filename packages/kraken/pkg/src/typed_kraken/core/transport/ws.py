"""WebSocket transport: Kraken Spot v2's request/reply-plus-channel-push socket.

Kraken correlates every reply -- subscribe/unsubscribe acks and trading-method replies
alike -- by the same client-supplied `req_id`, so `typed_core.ws.StreamsRpc` is a
direct fit: `request_subscription`/`request_unsubscription` are just `rpc_request` calls
with `method: "subscribe"`/`"unsubscribe"`.

One `KrakenSocketClient` class backs both the public (`ws.kraken.com/v2`) and private
(`ws-auth.kraken.com/v2`) connections -- the only difference is whether it was built
with a `token_cache`/`fetch_token` pair, mirroring how `transport/http.py`'s
`credentials` field alone distinguishes public/private HTTP calls on one client class.
When present, the token is merged into every outgoing `params` (subscribe requests and
RPC calls alike), since Kraken attaches it the same way in both cases.
"""

from typing_extensions import (
  Any,
  Awaitable,
  Callable,
  Literal,
  Mapping,
  NotRequired,
  TypeVar,
  cast,
)
from dataclasses import dataclass, field
from datetime import timedelta
import json

from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from typed_core.ws import StreamsRpc
from typed_core.ws.streams_rpc import Message, Response, Subscription

from ..auth import AuthResult, TokenCache
from ..endpoint.socket import SocketClient
from ..envelope import raise_error

T = TypeVar('T')

SPOT_WS_URL = 'wss://ws.kraken.com/v2'
SPOT_WS_AUTH_URL = 'wss://ws-auth.kraken.com/v2'


class Notification(TypedDict):
  """One channel push: a subscription snapshot/update, or the automatic `heartbeat`
  (which carries no `type`/`data`).
  """

  channel: str
  type: NotRequired[Literal['snapshot', 'update']]
  data: NotRequired[Any]


class MethodReply(TypedDict):
  """The reply to a `req_id`-correlated request: a trading-method call, or a
  subscribe/unsubscribe acknowledgement.
  """

  method: str
  req_id: int
  success: bool
  result: NotRequired[Any]
  error: NotRequired[str]
  time_in: NotRequired[str]
  time_out: NotRequired[str]


@dataclass
class SocketConnection(
  StreamsRpc[
    dict, MethodReply, Notification, Mapping[str, Any], MethodReply, MethodReply
  ]
):
  url: str = SPOT_WS_URL
  token_source: 'Callable[[], Awaitable[str]] | None' = None
  """Bound to `TokenCache.get(...)` by the owning `KrakenSocketClient`; `None` on the
  public connection.
  """

  async def send(self, msg: dict):
    ws = await self.ws
    await ws.send(json.dumps(msg))

  async def rpc_send(self, id: int, req: dict, /):
    if self.token_source is not None:
      req = {
        **req,
        'params': {**req.get('params', {}), 'token': await self.token_source()},
      }
    await self.send({**req, 'req_id': id})

  def parse_msg(
    self, msg: str | bytes, /
  ) -> 'Message[MethodReply, Notification] | None':
    obj = json.loads(msg)
    if 'req_id' in obj:
      return Response(
        kind='response', id=obj['req_id'], response=cast(MethodReply, obj)
      )
    if 'channel' in obj:
      return Subscription(
        kind='subscription',
        channel=obj['channel'],
        notification=cast(Notification, obj),
      )
    return None

  async def request_subscription(
    self, channel: str, params: Mapping[str, Any] | None = None
  ) -> MethodReply:
    reply = await self.rpc_request(
      {'method': 'subscribe', 'params': {'channel': channel, **(params or {})}}
    )
    if not reply['success']:
      raise_error([reply.get('error', f'subscribe "{channel}" failed')])
    return reply

  async def request_unsubscription(
    self, channel: str, params: Mapping[str, Any] | None = None
  ) -> MethodReply:
    reply = await self.rpc_request(
      {'method': 'unsubscribe', 'params': {'channel': channel, **(params or {})}}
    )
    if not reply['success']:
      raise_error([reply.get('error', f'unsubscribe "{channel}" failed')])
    return reply


@dataclass(kw_only=True)
class KrakenSocketClient(SocketClient):
  """Kraken Spot WebSocket v2 client, owning connection, token auth and validation --
  backs both `StreamEndpoint` (channel subscriptions) and `WsRpcEndpoint` (trading
  methods).
  """

  conn: SocketConnection = field(default_factory=SocketConnection)
  validate: bool = True

  @classmethod
  def new(
    cls,
    url: str = SPOT_WS_URL,
    *,
    token_cache: TokenCache | None = None,
    fetch_token: 'Callable[[], Awaitable[AuthResult]] | None' = None,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    ping_interval: timedelta = timedelta(seconds=30),
  ):
    """Build one connection. Thin: no environment lookup -- the root's `.new()` owns
    that.

    Args:
      url: `SPOT_WS_URL` for the public connection, `SPOT_WS_AUTH_URL` for the private
        one.
      token_cache: Set together with `fetch_token` for the private connection; both
        `None` for the public connection.
      fetch_token: Bound to the Spot HTTP client's `get_ws_token`.
    """
    token_source = None
    if token_cache is not None and fetch_token is not None:
      token_source = lambda: token_cache.get(fetch_token)  # noqa: E731
    conn = SocketConnection(
      url=url, timeout=timeout, ping_interval=ping_interval, token_source=token_source
    )
    return cls(conn=conn, validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate

  async def __aenter__(self):
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    manager = self.conn.subscribe(channel, params)
    if validator is None or not self.should_validate(validate):
      return cast(StreamManager[T, Any, Any], manager)
    return manager.map(validator)

  async def request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    reply = await self.conn.rpc_request(
      {'method': method, 'params': dict(params or {})}
    )
    if not reply['success']:
      raise_error([reply.get('error', f'"{method}" failed')])
    result = reply.get('result')
    if validator is not None and self.should_validate(validate):
      return validator.python(result)
    return cast(T, result)

  async def raw_request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    reply = await self.conn.rpc_request(
      {'method': method, 'params': dict(params or {})}
    )
    # `success` itself is absent from a whole-frame reply that has nothing to fail on --
    # `ping`'s real `pong` never carries it (see its endpoint spec's own notes) -- so a
    # missing key means success, and only an explicit `false` raises.
    if reply.get('success') is False:
      raise_error([reply.get('error', f'"{method}" failed')])
    if validator is not None and self.should_validate(validate):
      return validator.python(reply)
    return cast(T, reply)
