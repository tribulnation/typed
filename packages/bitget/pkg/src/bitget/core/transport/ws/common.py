"""Shared subscribe/unsubscribe/login/ping mechanics behind both `ClassicStreams` and
`UtaStreams`, plus id-correlated trade commands (`place-order`/`cancel-order`, Classic
only today). The one genuine structural fork between the two generations is the wire
shape of a subscription `arg` (`channel`+`instId` vs `topic`+`symbol`, see `spec/core.md`
WebSocket) — everything else here is identical, so it lives in one place and
`transport/ws/classic.py`/`uta.py` each supply only that shape via `build_arg`/`channel_of`.

Bitget mixes two correlation strategies on one connection: subscribe/unsubscribe/login
acks carry no id at all, matched purely by arrival order (`_ack_request`, a private mirror
of `typed_core.ws.SerialReplies` — not composed directly, since its own `replies:
asyncio.Queue` field collides by name with `StreamsRpc`'s own `replies: dict[int, Future]`,
and the two would silently clobber each other under dataclass field merging); a trade
command carries a real caller-visible `id`, matched via `StreamsRpc`'s own internal
`rpc_request` counter — `rpc_send` renders the counter's `int` id as the wire `str` id,
`parse_msg` reads it back off the echoed reply.
"""

from typing_extensions import Any, Callable, ClassVar, Mapping, TypeVar, cast
from abc import abstractmethod
from dataclasses import dataclass, field
import asyncio
import json
import time

from typed_core.exceptions import ApiError, AuthError, BadRequest
from typed_core.util import StreamManager
from typed_core.ws import StreamsRpc
from typed_core.ws.streams_rpc import Message
from typed_core.validation import validator

from ...endpoint.stream import StreamClient
from ...auth import Credentials, ws_login_args

T = TypeVar('T')

Notification = Mapping[str, Any]
"""One push frame: `{action, arg, data, ts}` — no `event` key, unlike replies below."""

SubscriptionParams = Mapping[str, Any]
"""The generation-specific field names a subscription needs, e.g. `{"instType": "SPOT",
"instId": "BTCUSDT"}` for Classic or `{"instType": "spot", "symbol": "BTCUSDT"}` for Uta —
merged into the wire `arg` by `build_arg`, never translated between generations."""

Reply = Mapping[str, Any]
"""One `{event: "subscribe"|"unsubscribe"|"login"|"error", ...}` ack frame, or a
`{event: "trade"|"error", arg: [...], code, msg}` command reply."""

Command = Mapping[str, Any]
"""One outgoing `{op: "trade", args: [{...}]}` command frame, `id` omitted — `rpc_send`
injects the connection-managed correlation id into `args[0]` before sending."""


@dataclass
class BaseSocketConnection(StreamsRpc[Command, Reply, Notification, SubscriptionParams, Reply, Reply]):
  """One physical connection's worth of subscribe/unsubscribe/login/ping mechanics, plus
  id-correlated trade commands.

  Requires implementing:
    `build_arg`: turn a wire channel name plus generation-specific params into the actual
      `arg` object sent in a `subscribe`/`unsubscribe` request.
    `channel_of`: read the wire channel name back out of an incoming push `arg`, so
      pushes route to the right local subscription.
  """

  _ack_queue: 'asyncio.Queue[Reply]' = field(default_factory=asyncio.Queue, init=False, repr=False)
  _ack_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  async def send(self, msg: object):
    ws = await self.ws
    await ws.send(json.dumps(msg))

  async def ping(self, ws):
    """Bitget's heartbeat is a literal raw string, not a JSON frame."""
    await ws.send('ping')

  @abstractmethod
  def build_arg(self, channel: str, params: SubscriptionParams) -> dict[str, Any]: ...

  @abstractmethod
  def channel_of(self, arg: Mapping[str, Any]) -> str: ...

  async def _ack_request(self, msg: object) -> Reply:
    """Send one subscribe/unsubscribe/login request and return the next reply by arrival
    order alone — mirrors `typed_core.ws.SerialReplies.request` (not reused directly, see
    the module docstring for why).
    """
    async with self._ack_lock:
      await self.send(msg)
      return await self._ack_queue.get()

  async def rpc_send(self, id: int, req: Command, /):
    arg = {**req['args'][0], 'id': str(id)}
    await self.send({**req, 'args': [arg]})

  def parse_msg(self, msg: str | bytes) -> 'Message[Reply, Notification] | None':
    if msg == 'pong':
      return None
    obj = json.loads(msg)
    if 'action' in obj:
      return {'kind': 'subscription', 'channel': self.channel_of(obj.get('arg', {})), 'notification': obj}
    if obj.get('event') in ('trade', 'error'):
      arg = obj.get('arg')
      command_id = arg[0].get('id') if isinstance(arg, list) and arg else None
      if command_id is not None:
        try:
          return {'kind': 'response', 'id': int(command_id), 'response': obj}
        except ValueError:
          pass
    self._ack_queue.put_nowait(obj)
    return None

  async def request_subscription(
    self, channel: str, params: SubscriptionParams | None = None
  ) -> Reply:
    reply = await self._ack_request(
      {'op': 'subscribe', 'args': [self.build_arg(channel, params or {})]}
    )
    if reply.get('event') == 'error':
      raise BadRequest(reply)
    if reply.get('event') != 'subscribe':
      raise ApiError(f'Expected "subscribe" reply, got {reply.get("event")!r}')
    return reply

  async def request_unsubscription(
    self, channel: str, params: SubscriptionParams | None = None
  ) -> Reply:
    reply = await self._ack_request(
      {'op': 'unsubscribe', 'args': [self.build_arg(channel, params or {})]}
    )
    if reply.get('event') == 'error':
      raise BadRequest(reply)
    if reply.get('event') != 'unsubscribe':
      raise ApiError(f'Expected "unsubscribe" reply, got {reply.get("event")!r}')
    return reply

  async def login(self, credentials: Credentials) -> Reply:
    """Send the login op and wait for its ack, sent once per connection before any private
    subscribe — not per-message. The WS timestamp is Unix seconds, unlike REST's milliseconds.
    """
    ts = str(int(time.time()))
    reply = await self._ack_request(
      {'op': 'login', 'args': [ws_login_args(credentials, timestamp=ts)]}
    )
    if reply.get('event') != 'login' or str(reply.get('code')) != '0':
      raise AuthError('WebSocket login failed', reply)
    return reply

  async def command(self, req: Command) -> Reply:
    """Send one id-correlated trade command (`place-order`/`cancel-order`) and return its
    reply, raising on an `event: "error"` result.
    """
    reply = await self.wait(self.rpc_request(req))
    if reply.get('event') == 'error':
      raise BadRequest(reply)
    return reply


@dataclass(kw_only=True)
class BaseSocketStreamClient(StreamClient):
  """WebSocket stream client, transparently routing between Bitget's two physical
  connections — mirroring how `HttpRpcClient.request`/`authed_request` share one class
  despite different auth-requiredness, `subscribe()` always uses `public_conn`,
  `authed_subscribe()` always uses `private_conn` (lazily logging in there first); not a
  public/private split at the owning `StreamEndpoint`, just which connection a call uses.

  Requires implementing (as a class attribute on the subclass):
    `symbol_key`: the params key holding the per-subscription symbol (`"instId"` for
      Classic, `"symbol"` for Uta) — used only to disambiguate concurrent subscriptions to
      the same channel with different symbols, never sent as-is if absent.
  """

  symbol_key: ClassVar[str]

  public_conn: BaseSocketConnection
  private_conn: BaseSocketConnection
  credentials: Credentials | None = None
  """`None` means unauthenticated: `authed_subscribe`/`authed_command` raises once connected."""
  validate: bool = True
  _logged_in: asyncio.Event = field(
    default_factory=asyncio.Event, init=False, repr=False
  )
  _login_lock: asyncio.Lock = field(
    default_factory=asyncio.Lock, init=False, repr=False
  )

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate

  async def __aenter__(self):
    await self.public_conn.__aenter__()
    await self.private_conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.public_conn.__aexit__(exc_type, exc_value, traceback)
    await self.private_conn.__aexit__(exc_type, exc_value, traceback)

  async def ensure_login(self):
    """Log in on the private connection if not already logged in, serialized against
    concurrent callers so several private subscribes racing on first use log in once.
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    if self._logged_in.is_set():
      return
    async with self._login_lock:
      if self._logged_in.is_set():
        return
      await self.private_conn.login(self.credentials)
      self._logged_in.set()

  def _local_key_and_message_key(
    self, channel: str, params: SubscriptionParams | None
  ) -> 'tuple[str, Callable[[Notification], str] | None]':
    symbol = (params or {}).get(self.symbol_key)
    if symbol is None:
      return channel, None
    local_key = f'{channel}:{symbol}'
    symbol_key = self.symbol_key

    def message_key(notification: Notification) -> str:
      return f'{channel}:{notification.get("arg", {}).get(symbol_key)}'

    return local_key, message_key

  def subscribe(
    self,
    channel: str,
    params: SubscriptionParams | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    local_key, message_key = self._local_key_and_message_key(channel, params)
    manager = self.public_conn.subscribe(
      local_key, params, request_channel=channel, message_key=message_key
    )
    if validator is None or not self.should_validate(validate):
      return cast('StreamManager[T, Any, Any]', manager)
    return manager.map(validator)

  def authed_subscribe(
    self,
    channel: str,
    params: SubscriptionParams | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    local_key, message_key = self._local_key_and_message_key(channel, params)

    async def connect():
      await self.ensure_login()
      return await self.private_conn.subscribe(
        local_key, params, request_channel=channel, message_key=message_key
      )

    manager = StreamManager(connect)
    if validator is None or not self.should_validate(validate):
      return cast('StreamManager[T, Any, Any]', manager)
    return manager.map(validator)

  async def authed_command(
    self,
    req: Command,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Log in if needed, then send one id-correlated trade command on the private
    connection and return its reply, validating it against `validator` if given.
    """
    await self.ensure_login()
    reply = await self.private_conn.command(req)
    if validator is None or not self.should_validate(validate):
      return cast(T, reply)
    return validator.python(reply)
