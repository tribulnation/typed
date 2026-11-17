"""WebSocket transport: the RISEx feed's frames and the subscribe/unsubscribe client.

One connection carries every subscription. Requests are `{"method", "params"}` frames;
their replies carry no correlation id but arrive in request order, so they are matched by
arrival (`SerialReplies`). Channel data is told apart from replies by its `type`
(`snapshot`/`update`) and routed by `channel`. The venue keeps one filter per channel (a
second subscribe would replace it), so the client holds at most one subscription per channel:
subscribing to a channel that is already open raises `RuntimeError`; unsubscribe first to
change its filter.

Private channels need the connection authenticated first (`auth_v2`: the signer signs
`RegisterV2` over a one-time nonce from `GET /v1/auth/nonce`); authentication lasts for the
connection, and is redone on the next one.
"""

from typing_extensions import Any, Literal, Mapping, NotRequired, TypeVar, cast
from dataclasses import dataclass, field, replace
from datetime import timedelta
import asyncio
import json

from typed_core.util import Stream, StreamManager
from typed_core.validation import TypedDict, validator
from typed_core.ws import SerialReplies, Streams
from typed_core.ws.socket import Context
from typed_core.ws.streams import Subscription

from ..endpoint.stream import StreamAuth, StreamClient
from ..exc import ApiError, AuthError, BadRequest
from ..signing import Api, Signing

T = TypeVar('T')
R = TypeVar('R')

AUTH_MESSAGE = 'WebSocket Authentication'
"""`message` signed into the `auth_v2` handshake."""

MAX_FRAME = 64 * 2**20
"""Largest frame accepted, in bytes. An unfiltered `orders` snapshot (every resting order
of every account) measured ~4.5 MB on testnet, far past `websockets`' 1 MiB default."""


class Params(TypedDict):
  """What `request_subscription` sends for one channel."""

  filter: Mapping[str, Any]
  """`market_ids`/`makers`, sent beside `channel`."""
  auth: NotRequired[StreamAuth]
  """Authenticate the connection first."""


class Notification(TypedDict):
  """One frame of channel data: a full `snapshot`, or an incremental `update`."""

  channel: str
  type: Literal['snapshot', 'update']


class Reply(TypedDict):
  """A reply to `subscribe`, `unsubscribe` or `auth_v2`.

  `type` names the request (`subscribed`/`unsubscribed`, absent on an auth reply), not its
  outcome: a rejected subscribe still says `subscribed`. `status` is the outcome.
  """

  method: str
  status: Literal['success', 'error']
  message: str
  type: NotRequired[str]
  channel: NotRequired[str]
  data: NotRequired[Any]


validate_reply = validator(Reply)


@dataclass
class SocketConnection(
  SerialReplies[Reply],
  Streams[Notification, Params, Reply, Reply],
):
  """The one physical connection to the feed."""

  signing: Signing | None = field(default=None, kw_only=True)
  """Credentials and signing state, for `auth_v2`; `None` for a public-only client."""
  api: Api | None = field(default=None, kw_only=True, repr=False)
  """The REST transport, for `auth_v2`'s one-time nonce."""
  authed: Context | None = field(default=None, init=False, repr=False)
  """The connection `auth_v2` succeeded on, if any."""
  auth_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  async def send(self, msg: object):
    """Write one JSON frame."""
    ws = await self.ws
    await ws.send(json.dumps(msg))

  def parse_msg(self, msg: str | bytes) -> Subscription[Notification] | None:
    """Route channel data to its subscription and replies to the waiting request; drop
    `pong`s and anything unrecognized.
    """
    obj = json.loads(msg)
    if not isinstance(obj, dict):
      return None
    if 'status' in obj:
      self.replies.put_nowait(validate_reply.python(obj))
    elif obj.get('type') in ('snapshot', 'update') and isinstance(
      obj.get('channel'), str
    ):
      return {'channel': obj['channel'], 'notification': cast(Notification, obj)}

  def connection_closed(self, ctx: Context):
    """Forget the closed connection's authentication."""
    if self.authed is ctx:
      self.authed = None
    super().connection_closed(ctx)

  def can_authenticate(self) -> bool:
    """Whether this client has the keys `auth_v2` needs."""
    credentials = self.signing.credentials if self.signing is not None else None
    return credentials is not None and credentials.signer_key is not None

  async def authenticate(self):
    """Authenticate the current connection with `auth_v2`, once per connection.

    Raises:
      AuthError: No signer key is configured, or the venue rejected the handshake (the
        signer is not active for the account, say).
    """
    async with self.auth_lock:
      ctx = await self.ctx
      if self.authed is ctx:
        return
      if self.signing is None or self.api is None:
        raise AuthError(
          'This channel needs authentication: build the client with keys.'
        )
      params = await self.signing.ws_auth(self.api, AUTH_MESSAGE)
      reply = await self.request({'method': 'auth_v2', 'params': params})
      if reply['status'] != 'success':
        raise AuthError(reply['message'], reply)
      self.authed = ctx

  async def request_subscription(
    self, channel: str, params: Params | None = None
  ) -> Reply:
    """Subscribe to `channel`, authenticating the connection first if asked to.

    Raises:
      AuthError: The channel needs authentication and it failed.
      BadRequest: The venue rejected the subscription.
    """
    auth = params.get('auth') if params else None
    if auth == 'required' or (auth == 'optional' and self.can_authenticate()):
      await self.authenticate()
    msg = {'channel': channel, **(params['filter'] if params else {})}
    reply = await self.request({'method': 'subscribe', 'params': msg})
    return self.check(reply, 'subscribe')

  async def request_unsubscription(
    self, channel: str, params: Params | None = None
  ) -> Reply:
    """Unsubscribe from `channel`.

    Raises:
      BadRequest: The venue rejected the request.
    """
    reply = await self.request(
      {'method': 'unsubscribe', 'params': {'channel': channel}}
    )
    return self.check(reply, 'unsubscribe')

  def check(self, reply: Reply, method: str) -> Reply:
    """Return a successful reply to `method`, raising on an error or a mismatched reply.

    Raises:
      BadRequest: The venue answered `status: error`.
      ApiError: The reply answers a different request.
    """
    if reply['method'] != method:
      raise ApiError(f'Expected a reply to {method!r}, got {reply!r}')
    if reply['status'] != 'success':
      raise BadRequest(reply['message'], reply)
    return reply


@dataclass(kw_only=True)
class SocketStreamClient(StreamClient):
  """WebSocket client: the shared connection, authentication and validation."""

  conn: SocketConnection
  """The physical connection."""
  validate: bool = True
  """Validate pushed messages by default."""

  @classmethod
  def new(
    cls,
    url: str,
    *,
    signing: Signing | None = None,
    api: Api | None = None,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
  ):
    """Build the transport. The server pings every 30 s and `websockets` answers on its
    own, so no application-level keep-alive is needed.

    Args:
      url: Feed URL.
      signing: Credentials and signing state, for `auth_v2`.
      api: The REST transport, for `auth_v2`'s nonce.
      validate: Validate pushed messages by default.
      timeout: Connection handshake timeout.
    """
    conn = SocketConnection(
      url, timeout=timeout, max_size=MAX_FRAME, signing=signing, api=api
    )
    return cls(conn=conn, validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self):
    """Take ownership of the connection without connecting (it opens on first use)."""
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection, ending every subscription on it."""
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    auth: StreamAuth | None = None,
    validator: validator[T] | None = None,
    reply_validator: validator[R] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, R, Any]:
    """Subscribe to `channel`, validating each frame against `validator` and the
    subscribe acknowledgement against `reply_validator`, when given and validation is on.
    """
    sub: Params = {'filter': params or {}}
    if auth is not None:
      sub['auth'] = auth
    manager = self.conn.subscribe(channel, sub)
    if not self.should_validate(validate):
      return cast(StreamManager[T, R, Any], manager)

    async def connect() -> Stream[T, R, Any]:
      """Subscribe, then validate the acknowledgement and wrap the pushes."""
      stream: Stream[Any, Any, Any] = await manager.connect()
      if reply_validator is not None:
        stream = replace(stream, reply=reply_validator.python(stream.reply))
      if validator is not None:
        stream = stream.map(validator)
      return stream

    return StreamManager(connect=connect)
