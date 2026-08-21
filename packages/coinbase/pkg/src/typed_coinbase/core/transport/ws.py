"""WebSocket transport, shared by the public market-data connection and the private
user connection — same host family, same envelope, same subscribe/unsubscribe shape.

Verified live: a data/ack message is `{channel, timestamp, sequence_num, events}` —
`channel: "subscriptions"` acknowledges the most recent (un)subscribe. A *rejected*
(un)subscribe is a completely different shape, `{"type": "error", "message": "..."}`, no
`channel` at all: an unrecognized channel name and an invalid `jwt` both came back
`{"type":"error","message":"authentication failure"}`; a malformed request came back
`{"type":"error","message":"subscribe or unsubscribe required"}`.

Neither carries a ordinary sequence number, so there is nothing to correlate a reply
against by id. `SerialReplies` correlates by strict ordering instead — one request in
flight per connection at a time — but only works because `parse_msg` below routes both
control shapes (`subscriptions` ack and `type: "error"`) into `self.replies`, and
everything else into the per-channel notification queues: verified live, an ordinary
`ticker` data event arrived *before* its own `subscriptions` ack, so a design that
naively took "the next message on the wire" as the reply would have grabbed that data
event instead.

Two more live-verified quirks, both specific to `level2`:

1. **The push channel tag doesn't match the subscribe channel name.** Subscribing sends
   `channel: "level2"`, but every pushed update carries `channel: "l2_data"` instead —
   confirmed live: 300+ real `l2_data` frames arrived on the wire while a subscriber
   listening under the local key `"level2"` (`Streams.on_msg` matches incoming
   `res['channel']` against the key `subscribe()` was called with) received zero of them.
   `typed_core.ws.streams.Streams.subscribe` already has a mechanism for exactly this: its
   local routing key (`channel`, matched against each incoming frame's own `channel`) and
   the value actually sent on the wire (`request_channel`) are two independent parameters.
   `CoinbaseSocketClient.subscribe` below swaps them for `level2` via `_PUSH_CHANNEL_TAGS`
   — local key `"l2_data"` (what arrives), `request_channel="level2"` (what's sent) — so no
   client-side remapping of the wire frame itself is needed; `Streams` does the routing.
2. **BTC-USD's initial `l2_data` snapshot is ~5MB**, past `websockets`' 1MB default
   `max_size` — confirmed live, subscribing with the base `Socket.force_open`'s hardcoded
   `websockets.connect(...)` call raised `ConnectionClosedError: message too big` before
   quirk 1 even got a chance to matter. `SocketConnection.force_open` below overrides just
   this connection's `max_size` rather than changing `typed_core.ws.socket.Socket`'s
   process-wide default for every client built on it.
"""

from typing_extensions import Any, Literal, Mapping, TypeVar, cast
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json
import websockets

from typed_core.exceptions import AuthError, BadRequest, NetworkError
from typed_core.validation import TypedDict, validator
from typed_core.util import StreamManager
from typed_core.ws import SerialReplies, Streams
from typed_core.ws.socket import Context
from typed_core.ws.streams import Subscription

from ..endpoint.stream import StreamClient
from ..auth import Credentials, ws_jwt

T = TypeVar('T')

MARKET_DATA_URL = 'wss://advanced-trade-ws.coinbase.com'
"""Public channels: `heartbeats`, `candles`, `status`, `ticker`, `ticker_batch`, `level2`,
`market_trades`."""

USER_URL = 'wss://advanced-trade-ws-user.coinbase.com'
"""Private channels: `user`, `futures_balance_summary`."""


class Msg(TypedDict):
  """A data notification, or a `subscriptions` acknowledgement (`channel: "subscriptions"`)."""

  channel: str
  timestamp: str
  sequence_num: int
  events: list[Any]


class ErrorFrame(TypedDict):
  """A rejected (un)subscribe request, or a malformed one. Carries no `channel` — see
  the module docstring for the two message texts observed live.
  """

  type: Literal['error']
  message: str


validate_msg = validator(Msg)
validate_error = validator(ErrorFrame)

_PUSH_CHANNEL_TAGS = {'level2': 'l2_data'}
"""Maps a channel name as passed to `subscribe()`/documented by Coinbase, to the
different tag its pushed frames actually carry — see module docstring, quirk 1. Passed
to `Streams.subscribe` as its local routing key, with the documented name sent on the
wire via `request_channel` instead."""


def _parse(msg: str | bytes) -> Msg | ErrorFrame:
  """Validate one wire message against whichever of the two shapes it actually is —
  `Msg | ErrorFrame` as one `validator` would ask pydantic to structurally discriminate a
  `TypedDict` union, which is more fragile than just checking for `type` up front.
  """
  raw = json.loads(msg)
  if isinstance(raw, dict) and raw.get('type') == 'error':
    return validate_error.python(raw)
  return validate_msg.python(raw)


def _check(reply: Msg | ErrorFrame) -> Msg:
  """Raise on a rejected (un)subscribe; pass a real ack through unchanged."""
  if 'type' in reply:
    if reply['message'] == 'authentication failure':
      raise AuthError(reply['message'])
    raise BadRequest(reply['message'])
  return reply


@dataclass
class SocketConnection(
  SerialReplies[Msg | ErrorFrame], Streams[Msg, Mapping[str, Any], Msg, Msg]
):
  """One physical connection."""

  url: str = MARKET_DATA_URL

  async def send(self, msg: object):
    ws = await self.ws
    await ws.send(json.dumps(msg))

  async def force_open(self):
    """Override the base's hardcoded `websockets.connect(...)` to lift `max_size` for
    this connection — `level2`'s initial snapshot can run ~5MB, past the library's 1MB
    default (see module docstring, quirk 2). Otherwise identical to
    `typed_core.ws.socket.Socket.force_open`.
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

  def parse_msg(self, msg: str | bytes) -> Subscription[Msg] | None:
    obj = _parse(msg)
    if 'type' in obj or obj['channel'] == 'subscriptions':
      self.replies.put_nowait(obj)
      return None
    return {'channel': obj['channel'], 'notification': obj}

  async def request_subscription(
    self, channel: str, params: Mapping[str, Any] | None = None
  ) -> Msg:
    return _check(
      await self.request({'type': 'subscribe', 'channel': channel, **(params or {})})
    )

  async def request_unsubscription(
    self, channel: str, params: Mapping[str, Any] | None = None
  ) -> Msg:
    return _check(
      await self.request({'type': 'unsubscribe', 'channel': channel, **(params or {})})
    )


@dataclass(kw_only=True)
class CoinbaseSocketClient(StreamClient):
  """WebSocket streams client, owning connection, authentication and validation."""

  conn: SocketConnection = field(default_factory=SocketConnection)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only public channels can be subscribed to."""
  validate: bool = True

  @classmethod
  def new(
    cls,
    url: str,
    *,
    credentials: Credentials | None = None,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
  ):
    """Build one subtree. Thin: no environment lookup — `Coinbase.new()` owns that."""
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
    local_channel = _PUSH_CHANNEL_TAGS.get(channel, channel)
    manager = self.conn.subscribe(local_channel, params, request_channel=channel)
    if validator is None or not self.should_validate(validate):
      return cast(StreamManager[T, Any, Any], manager)
    else:
      return manager.map(validator)

  def authed_subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to a private channel, embedding a fresh JWT in the subscribe message.

    The credential check and the JWT itself are both built lazily, inside the returned
    manager's own connect step — not here — so a manager built now and awaited later
    doesn't carry a JWT that has already gone stale past its 2-minute lifetime.

    Raises:
      AuthError: This transport was built with no credentials (`public=True` upstream).
    """

    async def connect():
      if self.credentials is None:
        raise AuthError('No credentials: this client was built with `public=True`.')
      full_params = {**(params or {}), 'jwt': ws_jwt(self.credentials)}
      return await self.conn.subscribe(channel, full_params)

    manager = StreamManager(connect)
    if validator is None or not self.should_validate(validate):
      return cast(StreamManager[T, Any, Any], manager)
    else:
      return manager.map(validator)
