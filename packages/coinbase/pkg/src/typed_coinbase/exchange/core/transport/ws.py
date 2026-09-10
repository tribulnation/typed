"""WebSocket Feed transport for Coinbase Exchange (formerly Pro/GDAX).

One physical connection serves both public and private channels — unlike Advanced Trade's
two-host split (`typed_coinbase.core.transport.ws`), Exchange has one feed host for the
standard tier. Verified live (2026-08-27, public channels only — no Exchange credentials
exist to test a private one):

- Subscribing sends `{"type": "subscribe", "channels": [...], "product_ids": [...]}`. A
  successful (un)subscribe acks with `{"type": "subscriptions", "channels": [...]}`,
  listing every channel now active on the connection.
- Every other frame carries its own `type` (`"heartbeat"`, `"ticker"`, `"l2update"`, ...)
  with no shared `channel` envelope field the way Advanced Trade's frames have — so
  `parse_msg` below derives the local routing key from `type` directly.
- A rejected (un)subscribe — bad channel name or bad product id, confirmed live for both —
  comes back as `{"type": "error", "message": "Failed to subscribe", "reason": "..."}`,
  **immediately followed by a second frame**, `{"type": "subscriptions", "channels": []}`.
  This second frame is a real protocol quirk `SerialReplies`'s one-reply-per-request model
  doesn't account for on its own: a plain `self.request(msg)` only consumes the first frame
  (the error) as this request's reply, leaving the trailing empty ack sitting in the reply
  queue to be wrongly picked up as the *next* (un)subscribe call's reply on this connection.
  Fixed here, locally: `_request_checked` below reimplements `SerialReplies.request`'s own
  send-then-await-one-reply body directly (rather than calling it), holding `self.lock` for
  the *whole* send-plus-drain, so draining the known-stale trailing ack on a caught
  rejection can never race a concurrent caller's own `send()` for the lock in between. This
  is exactly the venue-specific post-processing step `spec/core.md`'s gaps section called
  for -- no `SerialReplies`/`typed_core` change.

No credentials exist to verify the private-channel auth handshake. A `full`/`level2`/
`level3` snapshot's size is handled the same way Advanced Trade's `level2` needed (see
`typed_coinbase.core.transport.ws`'s module docstring): `force_open` below lifts
`max_size` for this one connection.
"""

from typing_extensions import Any, Literal, Mapping, NotRequired, TypeVar, TypedDict, cast
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json
import websockets

from typed_core.exceptions import AuthError, BadRequest, NetworkError
from typed_core.validation import validator
from typed_core.util import StreamManager
from typed_core.ws import SerialReplies, Streams
from typed_core.ws.socket import Context
from typed_core.ws.streams import Subscription

from typed_coinbase.core.endpoint.stream import StreamClient
from ..auth import Credentials, ws_auth_fields

T = TypeVar('T')

FEED_URL = 'wss://ws-feed.exchange.coinbase.com'
"""Standard-tier WebSocket Feed. The paid low-latency `wss://ws-direct.exchange.coinbase.com`
tier and the sandbox host are both out of scope for now — see `spec/core.md`."""


class SubscriptionsAck(TypedDict):
  """
  Acknowledges the connection's current subscriptions — sent after every successful
  (un)subscribe, and again, with an empty `channels` list, after a rejected one (see
  module docstring).
  """

  type: Literal['subscriptions']
  channels: list[Any]


class ErrorFrame(TypedDict):
  """A rejected (un)subscribe request."""

  type: Literal['error']
  message: str
  reason: NotRequired[str]


Reply = SubscriptionsAck | ErrorFrame

validate_ack = validator(SubscriptionsAck)
validate_error_frame = validator(ErrorFrame)


def _parse_reply(raw: dict[str, Any]) -> Reply:
  """Validate a control frame (`subscriptions` ack or `error`) into its real shape."""
  if raw.get('type') == 'error':
    return validate_error_frame.python(raw)
  return validate_ack.python(raw)


def _check(reply: Reply) -> Reply:
  """Raise on a rejected (un)subscribe; pass a real ack through unchanged."""
  if reply['type'] == 'error':
    text = reply.get('reason') or reply['message']
    if 'auth' in text.lower():
      raise AuthError(text)
    raise BadRequest(text)
  return reply


_AMBIGUOUS_MESSAGE_TYPES: Mapping[str, tuple[str, ...]] = {
  'snapshot': ('level2_batch', 'level2', 'level3', 'full'),
  'l2update': ('level2_batch', 'level2', 'level3', 'full'),
  'match': ('matches', 'full', 'level3'),
  'last_match': ('matches',),
  'rfq_match': ('rfq_matches',),
  'ticker': ('ticker', 'ticker_batch'),
}
"""Raw `type` values that don't equal the channel name a caller actually subscribed to
(confirmed live/against captured examples), each mapped to the channel(s) that can produce
it. `level2`/`level2_batch` share `snapshot`/`l2update` verbatim, and `ticker`/`ticker_batch`
share `ticker` verbatim -- Coinbase's own wire protocol gives no per-message way to tell
them apart. `parse_msg` below resolves the ambiguity by picking whichever candidate is
actually an active local subscription; this is exact for the realistic case (one of the two
ever subscribed at a time, true of every verified example and every real caller so far) and
only degrades -- silently dropping messages for one side, the same failure this table fixes
-- if a caller ever subscribes to both members of one of these pairs on the same connection
simultaneously, which Coinbase's own docs present as alternatives, not a supported
combination."""


@dataclass
class SocketConnection(SerialReplies[Reply], Streams[Any, Mapping[str, Any], Reply, Reply]):
  """One physical connection, carrying both public and private channels."""

  url: str = FEED_URL

  async def send(self, msg: object):
    ws = await self.ws
    await ws.send(json.dumps(msg))

  async def force_open(self):
    """Override the base's hardcoded `websockets.connect(...)` to lift `max_size` for
    this connection -- a `full`/`level2`/`level3` snapshot can run large the same way
    Advanced Trade's `level2` did (see `typed_coinbase.core.transport.ws`'s module
    docstring, this client's precedented fix for the identical problem). Otherwise
    identical to `typed_core.ws.socket.Socket.force_open`.
    """

    async def connect():
      try:
        return await websockets.connect(
          self.url, open_timeout=self.timeout.total_seconds(), max_size=None
        )
      except websockets.exceptions.WebSocketException as e:
        raise NetworkError(f'Failed to connect to {self.url}') from e

    ws = await connect()
    return Context(
      ws=ws,
      listener=asyncio.create_task(self.listener(ws)),
      pinger=asyncio.create_task(self.pinger(ws)),
    )

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    raw: dict[str, Any] = json.loads(msg)
    kind = raw['type']
    if kind in ('subscriptions', 'error'):
      self.replies.put_nowait(_parse_reply(raw))
      return None
    channel = kind
    for candidate in _AMBIGUOUS_MESSAGE_TYPES.get(kind, ()):
      if candidate in self.subscriptions:
        channel = candidate
        break
    notification: Subscription[Any] = {'channel': channel, 'notification': raw}
    return notification

  async def _request_checked(self, msg: object) -> Reply:
    """Send `msg` and return its reply, draining a known-stale trailing frame on a
    rejection -- see module docstring's WebSocket section.

    Reimplements `SerialReplies.request`'s own body (send, then await one reply) rather
    than calling it, so the extra drain runs under the *same* lock acquisition as the
    send: a rejected (un)subscribe here is always immediately followed by an extra,
    unsolicited `{"type": "subscriptions", "channels": []}` frame, and holding the lock
    across both reads means a concurrent caller's own `request()` can never send its
    message and observe that stale frame before this one drains it.
    """
    async with self.lock:
      await self.send(msg)
      reply = await self.replies.get()
      if reply['type'] == 'error':
        await self.replies.get()
      return reply

  async def request_subscription(
    self, channel: str, params: Mapping[str, Any] | None = None
  ) -> Reply:
    product_ids = (params or {}).get('product_ids')
    extra = {k: v for k, v in (params or {}).items() if k != 'product_ids'}
    msg: dict[str, Any] = {'type': 'subscribe', 'channels': [channel], **extra}
    if product_ids is not None:
      msg['product_ids'] = product_ids
    return _check(await self._request_checked(msg))

  async def request_unsubscription(
    self, channel: str, params: Mapping[str, Any] | None = None
  ) -> Reply:
    product_ids = (params or {}).get('product_ids')
    msg: dict[str, Any] = {'type': 'unsubscribe', 'channels': [channel]}
    if product_ids is not None:
      msg['product_ids'] = product_ids
    return _check(await self._request_checked(msg))


@dataclass(kw_only=True)
class ExchangeSocketClient(StreamClient):
  """WebSocket Feed client, owning connection, authentication and validation."""

  conn: SocketConnection = field(default_factory=SocketConnection)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only public channels can be subscribed to."""
  validate: bool = True

  @classmethod
  def new(
    cls,
    *,
    credentials: Credentials | None = None,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    url: str = FEED_URL,
  ):
    """Build the one connection. Thin: no environment lookup — `Exchange.new()` owns that."""
    conn = SocketConnection(url=url, timeout=timeout)
    return cls(conn=conn, credentials=credentials, validate=validate)

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

  def authed_subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to a private channel, embedding a fresh HMAC signature in the subscribe
    message.

    The credential check and the signature itself are both built lazily, inside the
    returned manager's own connect step — not here — matching Advanced Trade's
    `authed_subscribe`, for the same reason: a manager built now and awaited later
    shouldn't sign against a timestamp that's already stale by the time it connects.

    Raises:
      AuthError: This transport was built with no credentials (`exchange_public=True`
        upstream).
    """

    async def connect():
      if self.credentials is None:
        raise AuthError('No credentials: this client was built with `exchange_public=True`.')
      full_params = {**(params or {}), **ws_auth_fields(self.credentials)}
      return await self.conn.subscribe(channel, full_params)

    manager = StreamManager(connect)
    if validator is None or not self.should_validate(validate):
      return cast(StreamManager[T, Any, Any], manager)
    return manager.map(validator)
