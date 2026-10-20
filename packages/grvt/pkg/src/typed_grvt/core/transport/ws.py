"""JSON-RPC 2.0 WebSocket of one GRVT gateway (`wss://{gateway}/ws/full`).

One connection carries both request/reply RPCs and stream subscriptions:

- An RPC is `{"jsonrpc": "2.0", "method": "v1/<route>", "params", "id"}`; its reply echoes
  `id`, and its `result` is the whole HTTP body (`{"result": ...}`), so it is nested twice.
- Subscribe and unsubscribe are RPCs too (`method: "subscribe"`, `params: {stream,
  selectors}`), correlated by `id` like any other.
- Feed frames are not JSON-RPC: `{"stream", "selector", "sequence_number", "feed", ...}`.
  They are routed by `{stream}:{selector}`, which is exactly what was subscribed (verified
  live: the feed's `selector` echoes the subscribed one).
- The trading gateway authenticates the connection from its handshake headers only.
- A call the venue cannot parse is answered with `id` `0` and `method` `""` (verified on
  testnet: unparseable JSON, a non-object `params`, an id beyond 64 bits), so ids start at 1
  and such a reply is never matched to a call; every call waits at most `timeout` for its
  reply.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
import asyncio
import json
import logging

from typing_extensions import Any, TypedDict, cast

from typed_core.exceptions import AuthError, BadRequest, NetworkError
from typed_core.ws import StreamsRpc
from typed_core.ws.socket import BOUND, Context
from typed_core.ws.streams_rpc import Message

from ..auth import Session, SessionState
from ..envelope import UNAUTHENTICATED, check_rpc_frame

logger = logging.getLogger(__name__)


class RpcCall(TypedDict):
  """One JSON-RPC call, before an `id` is assigned."""

  method: str
  params: Any


class FeedFrame(TypedDict):
  """One pushed stream frame."""

  stream: str
  selector: str
  sequence_number: str
  """`"0"` for the initial snapshot frames only. Every later frame carries a counter that is
  per stream and selector and per gateway instance: it continues across connections and
  resets on a gateway restart. The subscribe reply's `first_sequence_number` is the first
  one to expect."""
  prev_sequence_number: str
  feed: Any


def channel_key(*, stream: str, selector: str) -> str:
  """Local routing key of one subscription: `{stream}:{selector}`."""
  return f'{stream}:{selector}'


def split_channel(channel: str) -> tuple[str, str]:
  """Split a `{stream}:{selector}` routing key.

  Raises:
    BadRequest: The channel names no selector.
  """
  stream, sep, selector = channel.partition(':')
  if not sep or not selector:
    raise BadRequest(f'Expected a "{{stream}}:{{selector}}" channel, got {channel!r}')
  return stream, selector


class Unauthenticated(AuthError):
  """The venue answered `1000` on a connection opened with a rejected session, or the call
  was refused before sending because its connection is known to be rejected. Either way the
  call was never processed: retire `ctx` and retry."""

  def __init__(self, ctx: Context, *args: object, sent: bool = True):
    """Record the rejected connection alongside the venue's error arguments.

    Args:
      ctx: The rejected connection.
      args: Exception arguments: the venue's code, message and frame.
      sent: Whether the call reached the venue.
    """
    super().__init__(*args)
    self.ctx = ctx
    """The rejected connection the call ran on."""
    self.sent = sent
    """Whether the call reached the venue (and was answered `1000`)."""


@dataclass(eq=False)
class Connection:
  """Session bookkeeping of one live trading connection."""

  ctx: Context
  opened_with: SessionState
  """Session the handshake carried."""
  idle: asyncio.Event = field(default_factory=asyncio.Event)
  """Set while no call sent on this connection awaits its reply."""
  pending: int = 0
  """Calls sent on this connection still awaiting their reply."""
  rejected: bool = False
  """The venue answered `1000` on this connection: it is never sent anything again."""
  retiring: 'asyncio.Future[None] | None' = None
  """Drains, then closes, this connection; started by the first `retire`."""

  def __post_init__(self):
    """Start idle: nothing has been sent on a new connection."""
    self.idle.set()


@dataclass
class GatewaySocket(
  StreamsRpc[RpcCall, dict[str, Any], FeedFrame, dict[str, Any], Any, Any]
):
  """One gateway's JSON-RPC WebSocket: RPCs and stream subscriptions on one connection.

  The trading gateway reads its session from the opening handshake only: it accepts any
  connection, then answers every call on an unauthenticated one with `1000` (verified live;
  query parameters and in-band login methods do not work). So, with a `session`, every
  connect first takes the current session (logging in if needed) and sends it as the
  handshake's `headers`, the same `Cookie`/`X-Grvt-Account-Id` the HTTP calls send.

  An open connection keeps the session it opened with. A call answered `1000` marks its
  connection rejected and raises `Unauthenticated`; its caller then `retire`s that
  connection (shared by every caller that saw it rejected: it is closed once, after the
  replies still pending on it have landed) and retries once on a fresh one. A call started
  meanwhile is never sent on the rejected connection.
  """

  headers: Mapping[str, str] | None = field(default=None, kw_only=True, repr=False)
  """Handshake headers. On the trading gateway these carry the session cookie, so they are
  left out of repr."""
  session: Session | None = field(default=None, kw_only=True)
  """Session authenticating the trading gateway's socket; `None` for market data."""
  connections: dict[int, Connection] = field(
    default_factory=dict, init=False, repr=False
  )
  """Session bookkeeping of each live connection, by `id()` of its `Context`."""
  checked: set[str] = field(default_factory=set, init=False, repr=False)
  """Channels whose replacement check passed and that were not released since."""
  counter: int = field(default=1, init=False, repr=False)
  """Next JSON-RPC id. Starts at 1: the venue answers a call it cannot parse with id `0`."""

  def connection(self, ctx: Context) -> Connection | None:
    """Session bookkeeping of `ctx`, if it is a live session-authenticated connection."""
    conn = self.connections.get(id(ctx))
    return conn if conn is not None and conn.ctx is ctx else None

  async def force_open(self) -> Context:
    """Connect, authenticating the handshake with the current session when there is one."""
    state = None
    if self.session is not None:
      state = await self.session.state()
      self.headers = state.headers
    ctx = await super().force_open()
    if state is not None:
      self.connections[id(ctx)] = Connection(ctx, state)
    return ctx

  def connection_closed(self, ctx: Context):
    """Forget the closed connection's session bookkeeping and replacement checks too."""
    if self.connection(ctx) is not None:
      del self.connections[id(ctx)]
    self.checked.clear()
    super().connection_closed(ctx)

  def reject(self, ctx: Context):
    """Record that the venue answered `1000` on `ctx`: forget the session it opened with
    (unless a newer one already replaced it) and send nothing more on it.

    Synchronous on purpose: it runs inside work bound to `ctx`, which closing `ctx` would
    cancel.
    """
    conn = self.connection(ctx)
    if self.session is None or conn is None:
      return
    conn.rejected = True
    self.session.invalidate(conn.opened_with)

  async def retire(self, ctx: Context):
    """Close a rejected connection once the replies pending on it have landed, so the next
    call opens a fresh one.

    Idempotent: every caller that saw `ctx` rejected awaits the same retirement, and a
    connection already closed is left alone. The drain waits at most `timeout`; a call
    whose reply is still pending then ends with `NetworkError` and is not retried, since it
    may have been processed. Live subscriptions on the closed connection end with
    `NetworkError` and must be resubscribed. Must not run inside work bound to `ctx`.
    """
    conn = self.connection(ctx)
    if conn is None:
      return
    if conn.retiring is None:
      conn.retiring = asyncio.ensure_future(self.drain_and_close(conn))
    await asyncio.shield(conn.retiring)

  async def drain_and_close(self, conn: Connection):
    """Wait (at most `timeout`) for no call to be pending on `conn`, then close it."""
    idle = asyncio.ensure_future(conn.idle.wait())
    try:
      await asyncio.wait([idle], timeout=self.timeout.total_seconds())
    finally:
      idle.cancel()
    await self.close(conn.ctx)

  async def rpc_send(self, id: int, req: RpcCall, /):
    """Send one JSON-RPC call."""
    ws = await self.ws
    await ws.send(
      json.dumps(
        {'jsonrpc': '2.0', 'method': req['method'], 'params': req['params'], 'id': id}
      )
    )

  def parse_msg(self, msg: str | bytes, /) -> Message[dict[str, Any], FeedFrame] | None:
    """Route a feed frame by `{stream}:{selector}`, a JSON-RPC reply by `id`.

    Anything else is logged and dropped, never raised: raising here would end the
    connection's listener, failing every call and stream on it. That includes an
    undecodable frame and a reply naming no call (id `0`, the venue's answer to a call it
    could not parse); the call it belonged to then ends with its reply timeout.
    """
    try:
      frame = json.loads(msg)
    except (json.JSONDecodeError, UnicodeDecodeError):
      logger.warning('Undecodable frame: %r', msg[:500])
      return None
    if not isinstance(frame, dict):
      logger.warning('Unexpected frame: %r', frame)
      return None
    if 'feed' in frame and 'stream' in frame and 'selector' in frame:
      return {
        'kind': 'subscription',
        'channel': channel_key(stream=frame['stream'], selector=frame['selector']),
        'notification': cast(FeedFrame, frame),
      }
    rpc_id = frame.get('id')
    if isinstance(rpc_id, int) and not isinstance(rpc_id, bool) and rpc_id > 0:
      return {'kind': 'response', 'id': rpc_id, 'response': frame}
    logger.warning('Reply matching no call: %r', frame)
    return None

  async def call(self, method: str, params: Any) -> Any:
    """Call one JSON-RPC method and return its `result`.

    Never sends on a connection known to be rejected: outside work bound to one, it waits
    for that connection's retirement and uses a fresh one; inside it (a subscribe), it
    raises `Unauthenticated` unsent.

    Args:
      method: JSON-RPC method, e.g. `v1/instrument` or `subscribe`.
      params: JSON-compatible params.

    Raises:
      Unauthenticated: The venue answered `1000` (the connection is then marked rejected,
        see `reject`), or the bound connection is already rejected; the caller retires
        `ctx` and may retry.
      NetworkError: The connection dropped, or no reply came within `timeout`; either way
        the call may have been processed.
      ApiError: The reply carried any other `error` (mapped by code, see
        `envelope.raise_code`).
    """
    while True:
      ctx = await self.ctx
      conn = self.connection(ctx)
      if conn is None or not conn.rejected:
        break
      bound = BOUND.get()
      if bound is not None and bound[0] is self:
        raise Unauthenticated(
          ctx, UNAUTHENTICATED, 'Connection rejected; not sent', sent=False
        )
      await self.retire(ctx)
    if conn is not None:
      conn.pending += 1
      conn.idle.clear()
    timeout = self.timeout.total_seconds()
    try:
      frame = await asyncio.wait_for(
        self.wait(self.rpc_request({'method': method, 'params': params}), ctx=ctx),
        timeout,
      )
    except asyncio.TimeoutError:
      raise NetworkError(
        f'No reply to {method} within {timeout:g} s; it may have been processed'
      ) from None
    finally:
      if conn is not None:
        conn.pending -= 1
        if not conn.pending:
          conn.idle.set()
    try:
      return check_rpc_frame(frame)
    except AuthError as e:
      if conn is not None and e.args and e.args[0] == UNAUTHENTICATED:
        self.reject(ctx)
        raise Unauthenticated(ctx, *e.args) from e
      raise

  def check_replacement(self, channel: str):
    """Refuse a subscription the venue would treat as replacing a live one, else claim its
    primary selector.

    Subscribing again with the same primary selector (the part before `@`) on the same
    stream replaces the earlier secondary selector, silently ending that subscription. Only
    subscriptions whose own check already passed count, and the scan and the claim run with
    no await between them, so of two concurrent subscribes to one primary selector exactly
    the first succeeds.

    Raises:
      BadRequest: Another live subscription shares this stream and primary selector.
    """
    stream, selector = split_channel(channel)
    primary = selector.split('@', 1)[0]
    for other in self.subscriptions:
      if other == channel or other not in self.checked:
        continue
      other_stream, other_selector = split_channel(other)
      if other_stream == stream and other_selector.split('@', 1)[0] == primary:
        raise BadRequest(
          f'{stream} {selector!r} would replace the live subscription {other_selector!r}: '
          'unsubscribe it first'
        )
    self.checked.add(channel)

  async def request_subscription(
    self, channel: str, params: dict[str, Any] | None = None
  ) -> Any:
    """Subscribe one selector, returning the venue's subscribe result.

    Args:
      channel: `{stream}:{selector}` routing key.
      params: Extra subscribe params, the parameters no channel placeholder consumed.
    """
    stream, selector = split_channel(channel)
    self.check_replacement(channel)
    try:
      result = await self.call(
        'subscribe', {'stream': stream, 'selectors': [selector], **(params or {})}
      )
      if selector not in (result or {}).get('subs', []):
        raise BadRequest(
          f'{stream} {selector!r} was not subscribed: the venue answered {result!r}'
        )
    except BaseException:
      self.checked.discard(channel)
      raise
    return result

  async def request_unsubscription(
    self, channel: str, params: dict[str, Any] | None = None
  ) -> Any:
    """Unsubscribe one selector, returning the venue's unsubscribe result.

    A connection the venue rejected (`1000`) is not unsubscribed on: it is retired, which
    ends the subscription, so the unsubscribe returns `None` instead of raising.

    Args:
      channel: `{stream}:{selector}` routing key.
      params: Unused: unsubscribing takes only the stream and selector.
    """
    stream, selector = split_channel(channel)
    self.checked.discard(channel)
    try:
      return await self.call('unsubscribe', {'stream': stream, 'selectors': [selector]})
    except Unauthenticated:
      # The connection is rejected: nothing more is sent on it, and it is closed before
      # the next call goes out, which ends this subscription with it.
      return None
