"""WebSocket transport for the Unified Trading Account (UTA) private channels.

UTA WebSocket V2 differs from the Classic bullet-token connections in `ws.py` on every
point that matters to a transport, so it is its own class rather than a mode of
`SocketConnection`:

1. A static host, `wss://wsapi-push.kucoin.com`, with no bullet-token call.
2. Signature authentication after connecting: an `op: auth` frame carrying the key, a
   millisecond timestamp, `HMAC(secret, timestamp + 'POST/api/websocket/users/verify')`
   and the HMAC-signed passphrase, answered `{"id": <session>, "result": true}`.
3. Subscriptions name a `channel` and a `tradeType` (`{"action": "SUBSCRIBE", "channel":
   "execution", "tradeType": "UNIFIED"}`), acknowledged `{"id", "result": true}` or
   `{"id", "result": false, "message"}`.
4. Pushes are `{"T": "<channel>.<tradeType>", "P": <push time>, "d": {...}}`, so the
   channel string a generated endpoint subscribes with is the pushes' own `T` value
   (`execution.UNIFIED`), split at its last `.` to build the subscribe frame.
5. Heartbeat `{"id", "op": "ping"}`, answered `{"op": "pong", "id", "ts"}`.

Checked live 2026-11-27 (on a Classic account, which this connection accepts too): the
welcome frame, authentication, subscribe and unsubscribe acknowledgements, an unknown
channel's refusal and the pong. See `spec/core.md` §UTA WebSocket.

References:
  - [UTA WebSocket introduction](https://www.kucoin.com/docs-new/websocket-api/introduction)
"""

from typing_extensions import Any, NotRequired, Self, TypeVar, cast
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json as _json
import time

from typed_core.exceptions import AuthError, BadRequest
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from typed_core.ws.socket import Context
from typed_core.ws.streams import Streams, Subscription

from ..auth import Credentials, sign
from ..endpoint.stream import StreamClient

T = TypeVar('T')

UTA_PRIVATE_WS_URL = 'wss://wsapi-push.kucoin.com'
"""Host of the UTA private push channels, for every product line."""
VERIFY_PATH = 'POST/api/websocket/users/verify'
"""Fixed method and path folded into the authentication signature."""
PING_INTERVAL = timedelta(seconds=18)
"""KuCoin's welcome frame recommends 18 000 ms; it drops a client pinging more than once a
second, and one that stays silent for long."""


class Push(TypedDict):
  """One channel push: the channel (`<channel>.<tradeType>`), push time and payload."""

  T: str
  P: NotRequired[int]
  d: Any


class Reply(TypedDict):
  """Acknowledges, or refuses, an `auth`, `SUBSCRIBE` or `UNSUBSCRIBE` frame."""

  id: NotRequired[str]
  result: bool | str
  """`true` (sometimes the string `"true"`) on success."""
  message: NotRequired[str]
  """Why it was refused."""


validate_push = validator(Push)
validate_reply = validator(Reply)


def _dumps(msg: Any) -> str:
  return _json.dumps(msg, separators=(',', ':'))


def accepted(reply: Reply) -> bool:
  """Whether an acknowledgement reports success."""
  return reply['result'] is True or reply['result'] == 'true'


def auth_frame(credentials: Credentials, *, timestamp: str) -> dict[str, str]:
  """The `op: auth` frame for one connection.

  Args:
    credentials: API key, secret and passphrase.
    timestamp: Millisecond timestamp, signed and sent.
  """
  return {
    'op': 'auth',
    'kc-api-key': credentials.api_key,
    'kc-api-timestamp': timestamp,
    'kc-api-sign': sign(credentials.api_secret, timestamp + VERIFY_PATH),
    'kc-api-passphrase': sign(credentials.api_secret, credentials.api_passphrase),
  }


def subscription_frame(action: str, channel: str, id: str) -> dict[str, str]:
  """A subscribe or unsubscribe frame for `channel`, written `<channel>.<tradeType>`.

  Raises:
    ValueError: `channel` has no `.<tradeType>` suffix.
  """
  name, sep, trade_type = channel.rpartition('.')
  if not sep or not name:
    raise ValueError(f'UTA channel {channel!r} must be written <channel>.<tradeType>')
  return {'id': id, 'action': action, 'channel': name, 'tradeType': trade_type}


@dataclass
class UtaPrivateConnection(Streams[Push, None, Reply, Reply]):
  """The one authenticated UTA private connection of a client.

  Opens lazily on the first subscription, authenticates before any subscribe is sent,
  and serializes commands so "the next reply" is the reply to the frame just sent: a
  push never carries `result`, so replies and pushes cannot be confused.
  """

  credentials: Credentials | None = field(default=None, kw_only=True, repr=False)
  counter: int = field(default=0, init=False, repr=False)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: 'asyncio.Queue[Reply]' = field(
    default_factory=asyncio.Queue, init=False, repr=False
  )

  def next_id(self) -> str:
    """A fresh request id for this connection."""
    self.counter += 1
    return str(self.counter)

  async def command(self, msg: Any, *, ctx: Context | None = None) -> Reply:
    """Send one frame and wait for its acknowledgement.

    Raises:
      BadRequest: KuCoin refused the frame.
    """
    async with self.lock:
      ws = ctx.ws if ctx is not None else await self.ws
      await ws.send(_dumps(msg))
      reply = await self.wait(self.replies.get(), ctx=ctx)
    if not accepted(reply):
      raise BadRequest(reply)
    return reply

  async def force_open(self):
    """Connect, then authenticate before handing the connection to any subscriber.

    Raises:
      AuthError: There are no credentials, or KuCoin refused them.
    """
    if self.credentials is None:
      raise AuthError(
        'UTA private channels require credentials; build the client with '
        '`KuCoin.new(api_key=..., api_secret=..., api_passphrase=...)`.'
      )
    self.replies = asyncio.Queue()
    ctx = await super().force_open()
    timestamp = str(int(time.time() * 1000))
    try:
      await self.command(auth_frame(self.credentials, timestamp=timestamp), ctx=ctx)
    except BadRequest as exc:
      await self.close(ctx)
      raise AuthError(*exc.args) from exc
    except BaseException:
      await self.close(ctx)
      raise
    return ctx

  async def ping(self, ws):
    """KuCoin's application-level ping."""
    await ws.send(_dumps({'id': self.next_id(), 'op': 'ping'}))

  def parse_msg(self, msg: str | bytes) -> Subscription[Push] | None:
    """Route a push by its `T`; queue acknowledgements; drop welcome and pong frames."""
    frame = _json.loads(msg)
    if isinstance(frame, dict):
      if 'T' in frame:
        push = validate_push.python(frame)
        return Subscription(channel=push['T'], notification=push)
      elif 'result' in frame:
        self.replies.put_nowait(validate_reply.python(frame))

  async def request_subscription(self, channel: str, params: None = None) -> Reply:
    """Subscribe to `channel`, written `<channel>.<tradeType>`."""
    return await self.command(subscription_frame('SUBSCRIBE', channel, self.next_id()))

  async def request_unsubscription(self, channel: str, params: None = None) -> Reply:
    """Unsubscribe from `channel`."""
    return await self.command(
      subscription_frame('UNSUBSCRIBE', channel, self.next_id())
    )


def _data(push: Push) -> Any:
  return push['d']


@dataclass(kw_only=True)
class UtaStreamClient(StreamClient):
  """Streams client over the UTA private connection: private channels only."""

  conn: UtaPrivateConnection
  validate: bool = True

  @classmethod
  def new(
    cls,
    *,
    credentials: Credentials | None,
    validate: bool = True,
    url: str = UTA_PRIVATE_WS_URL,
    timeout: timedelta = timedelta(seconds=10),
  ) -> Self:
    """Build the (unopened) connection.

    Args:
      credentials: The client's credentials; `None` for a public client, whose every
        subscription then raises `AuthError`.
      validate: Validate pushed payloads by default.
      url: Host override, for tests.
      timeout: Connect and pong timeout.
    """
    conn = UtaPrivateConnection(
      url, credentials=credentials, timeout=timeout, ping_interval=PING_INTERVAL
    )
    return cls(conn=conn, validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """UTA private connections carry no public channels.

    Raises:
      AuthError: Always.
    """
    raise AuthError(f'{channel} is a private UTA channel')

  def authed_subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to a private channel, validating each payload against `validator`.

    Raises:
      AuthError: The client has no credentials (raised when the stream opens).
    """
    if self.conn.credentials is None:
      raise AuthError(
        f'{channel} requires credentials; build the client with '
        '`KuCoin.new(api_key=..., api_secret=..., api_passphrase=...)`.'
      )
    manager = self.conn.subscribe(channel)
    if validator is not None and self.should_validate(validate):
      return manager.map(lambda push: validator.python(push['d']))
    return cast(StreamManager[T, Any, Any], manager.map(_data))
