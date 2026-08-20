"""Bybit v5 WebSocket transport primitives: connections, subscriptions and trade commands.

Bybit's v5 WebSocket surface is nine separate connections, not one: four public
category streams (`spot`, `linear`, `inverse`, `option`), Spread Trading's and RFQ
Trading's own public streams, Advanced Earn's fixed-price offer stream, one private
stream, and one order-entry ("WS Trade") connection — see
[the v5 WebSocket guide](https://bybit-exchange.github.io/docs/v5/ws/connect) and the
[WS Trade guideline](https://bybit-exchange.github.io/docs/v5/websocket/trade/guideline).

Every leaf sharing a connection shares the exact same `socket` instance, since a
`Streams`' subscription bookkeeping lives on that one object — there is no pool to hand
out fresh instances from the way `Endpoint.http` is shared. `bybit.ws` wires these
primitives up with real URLs, credentials and the channel/command classes.
"""

from typing_extensions import Any, NotRequired
from collections import deque
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json as _json
import time

from typed_core.exceptions import AuthError
from typed_core.ws.rpc import Response, Rpc
from typed_core.ws.streams import Streams, Subscription

from .auth import Credentials, ws_auth_args
from .mixin import BYBIT_DOMAINS, Region
from .validation import TypedDict, validator

WS_DEDICATED_REGIONS = frozenset({'tr', 'id', 'kz', 'ge', 'jp'})
"""Regions Bybit documents a dedicated WebSocket host for (`stream.<their domain>`).

Confirmed live against [the v5 WebSocket guide](https://bybit-exchange.github.io/docs/v5/ws/connect):
"If your account is registered from www.bybit.tr, please use stream.bybit.tr", and the same
pattern for `id`/`kz`/`ge`/`jp`. Every other region — `eu`, `nl`, `ae`, `bytick` included —
routes through the global stream instead, unlike REST where every region gets its own host.
"""


class WsUrls(TypedDict):
  """One resolved URL per Bybit v5 WebSocket connection."""

  spot: str
  linear: str
  inverse: str
  option: str
  spread: str
  rfq: str
  private: str
  trade: str
  fp: str
  """Advanced Earn's fixed-price offer channels (`finance.advanced_earn.websocket.*_offer`)
  -- named after the venue's own `/v5/public/fp` path segment, not the `finance` function
  root, matching every other key here."""


def resolve_ws_urls(region: Region, *, testnet: bool = False) -> WsUrls:
  """Return every WebSocket connection URL for one region.

  Unlike `resolve_rest_base_url`, most regions have no dedicated WebSocket host at all
  — see `WS_DEDICATED_REGIONS` — so this falls back to the global stream domain for
  every region not in that set, rather than building a same-shaped-but-unconfirmed URL
  the way the REST resolver does for an undocumented testnet host.

  Args:
    region: Legal entity to target.
    testnet: Target that region's testnet host instead of mainnet.

  Raises:
    ValueError: `region` is not one of `BYBIT_DOMAINS`.

  References:
    - [Bybit v5 WebSocket guide](https://bybit-exchange.github.io/docs/v5/ws/connect)
  """
  if region not in BYBIT_DOMAINS:
    known = ', '.join(repr(k) for k in BYBIT_DOMAINS)
    raise ValueError(f'Unknown Bybit region {region!r}. Expected one of {known}.')
  domain = BYBIT_DOMAINS[region if region in WS_DEDICATED_REGIONS else 'global']
  subdomain = 'stream-testnet' if testnet else 'stream'
  base = f'wss://{subdomain}.{domain}'
  return WsUrls(
    spot=f'{base}/v5/public/spot',
    linear=f'{base}/v5/public/linear',
    inverse=f'{base}/v5/public/inverse',
    option=f'{base}/v5/public/option',
    spread=f'{base}/v5/public/spread',
    rfq=f'{base}/v5/public/rfq',
    private=f'{base}/v5/private',
    trade=f'{base}/v5/trade',
    fp=f'{base}/v5/public/fp',
  )


AUTH_EXPIRY_MS = 10_000
"""How far into the future a WS `auth` signature's `expires` is set, in milliseconds."""

PING_INTERVAL = timedelta(seconds=20)
"""Bybit disconnects a socket that goes this long without a ping."""


class Frame(TypedDict):
  """Any frame Bybit sends on a public-category or private stream: a push, a
  subscribe/unsubscribe/auth ack, or a pong.

  Every field is optional because the shape actually varies by kind, and for pongs
  even by category — confirmed live/documented variants range from a full ack shape
  (`success`, `ret_msg`, `conn_id`, `op`) on spot/linear/inverse/private to a bare
  `{"args": [...], "op": "pong"}` on option/spread. That bare shape is the ping/pong
  keepalive reply only — `option`'s real subscribe/unsubscribe ack is a different
  shape entirely, `{"success", "conn_id", "data": {"failTopics", "successTopics"},
  "type": "COMMAND_RESP"}` (live-verified), carrying no `op` at all, so `is_pong`
  correctly does not mistake it for a pong and it already routes through `Reply` like
  every other category's ack. This type only proves a frame is well-formed enough to
  route; `Reply` re-validates the stricter ack shape once a frame is confirmed to be
  one, and `is_pong` (not this shape) decides that.
  """

  topic: NotRequired[str]
  data: NotRequired[Any]
  op: NotRequired[str]
  ret_msg: NotRequired[str]
  success: NotRequired[bool]
  conn_id: NotRequired[str]
  req_id: NotRequired[str]
  args: NotRequired[list]


validate_frame = validator[Frame](Frame)


class Reply(TypedDict):
  """Frame Bybit sends in answer to a `subscribe`, `unsubscribe` or `auth` command."""

  success: bool
  ret_msg: NotRequired[str]
  conn_id: NotRequired[str]
  req_id: NotRequired[str]
  op: NotRequired[str]


validate_reply = validator[Reply](Reply)


def is_pong(frame: 'Frame | TradeFrame') -> bool:
  """Bybit's pong shape isn't uniform: `op` is `"pong"` on private/option/spread, but
  an echoed `"ping"` on spot/linear/inverse, where `ret_msg == "pong"` is the reliable
  signal instead. Checking both covers every documented variant. Also accepts a
  `TradeFrame` -- the WS Trade connection's pong shape isn't documented separately, see
  `TradeFrame`'s own docstring -- since `BybitTradeClient.parse_response` reuses this
  same check to spot a `ping` command's reply."""
  return frame.get('op') in ('ping', 'pong') or frame.get('ret_msg') == 'pong'


def dumps(msg: Any) -> str:
  """Compact JSON encoding for an outgoing WebSocket frame."""
  return _json.dumps(msg, separators=(',', ':'))


@dataclass
class BybitStreamsClient(Streams[Any, Any, Reply, Reply]):
  """One public-category or private Bybit v5 stream connection.

  Multiplexes every channel subscribed on it, matching Bybit's own shape: `subscribe`/
  `unsubscribe` acks carry no id, so replies are matched by arrival order under a lock;
  pushes are routed by their `topic` field.
  """

  url: str
  ping_interval: timedelta = field(default=PING_INTERVAL)
  credentials: Credentials | None = field(default=None, kw_only=True, repr=False)
  """Set only for the private connection. `None` here means "don't authenticate", not
  "this connection has no private channels" — see `require_auth`."""
  require_auth: bool = field(default=False, kw_only=True)
  """True for the private connection: refuse to open at all without credentials, rather
  than dialing out and letting Bybit reject the first subscribe."""
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: 'asyncio.Queue[Reply]' = field(
    default_factory=asyncio.Queue, init=False, repr=False
  )

  async def send(self, msg: Any):
    """Send one JSON frame."""
    await (await self.ws).send(dumps(msg))

  async def command(self, msg: Any) -> Reply:
    """Send one command frame and wait for the ack answering it.

    Goes through `self.wait`, not a bare `self.replies.get()`, so a connection that
    dies before answering raises instead of leaving the caller waiting forever — safe
    to do here, unlike in `force_open`, since `command` only ever runs once the
    connection is already open and the listener task is actually running.
    """
    async with self.lock:
      await self.send(msg)
      return await self.wait(self.replies.get())

  async def ping(self, ws):
    await ws.send(dumps({'op': 'ping'}))

  async def force_open(self):
    """Connect, then authenticate before returning — so every subsequent subscribe is
    already past the handshake, and a channel that needs auth never gets a chance to
    race it.

    Waits on `self.replies` like any other command — safe now that
    `typed_core.ws.Socket.force_open` hands `listener`/`pinger` the live connection
    directly instead of having them resolve it via `self.ctx`, so the listener starts
    delivering the moment it's scheduled rather than blocking on this very call
    returning (see ADR 0005). Passes `ctx=ctx` to `self.wait(...)` rather than leaving it
    to resolve `self.ctx` on its own — `self.ctx` isn't resolved until this method
    returns, but `ctx` is exactly what this method already built, so a dead
    listener/pinger still raises here instead of only after `self.timeout` elapses. That
    timeout still wraps the whole wait, since a venue can also reject a request by never
    answering it at all, not just by dying or refusing it.

    `expires` in the signed `auth` frame is a replay window on the handshake frame
    itself — Bybit rejects it if it arrives after `expires` — not a session lifetime.
    Bybit doesn't document this either way, but it's now live-verified rather than
    assumed: a private connection held authenticated for 25 minutes (one `wallet`
    subscription plus a private command probed once a minute), the whole span on one
    `conn_id`, no re-auth needed. That evidence is bounded — not "never expires," just
    "didn't in 25 minutes" — but it rules out any short-lived (a few minutes)
    session-token-style expiry. What's covered: a connection that drops for any reason
    reopens through this same method and re-authenticates from scratch. What isn't:
    proof that this holds indefinitely, or a connection Bybit keeps open but silently
    stops honoring the auth on — nothing here would detect or recover from that.
    """
    if self.require_auth and self.credentials is None:
      raise AuthError(
        f'{self.url} is a private stream; build the client with '
        '`Bybit.new(api_key=..., api_secret=...)`.'
      )
    ctx = await super().force_open()
    if self.credentials is not None:
      expires = int(time.time() * 1000) + AUTH_EXPIRY_MS
      await ctx.ws.send(
        dumps({'op': 'auth', 'args': ws_auth_args(self.credentials, expires=expires)})
      )
      try:
        reply = await asyncio.wait_for(
          self.wait(self.replies.get(), ctx=ctx), timeout=self.timeout.total_seconds()
        )
      except asyncio.TimeoutError as e:
        raise AuthError(
          f'{self.url}: no reply to the auth frame within {self.timeout}'
        ) from e
      if not reply.get('success'):
        raise AuthError(f'Bybit WS auth failed: {reply.get("ret_msg")}', reply)
    return ctx

  async def request_subscription(self, channel: str, params: Any = None) -> Reply:
    """`channel` is the full topic string, e.g. `orderbook.50.BTCUSDT` or `wallet`."""
    return await self.command({'op': 'subscribe', 'args': [channel]})

  async def request_unsubscription(self, channel: str, params: Any = None) -> Reply:
    return await self.command({'op': 'unsubscribe', 'args': [channel]})

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    """Route a push by `topic`; anything else (subscribe/unsubscribe/auth acks, pongs)
    is a command reply."""
    frame = validate_frame(msg)
    if 'topic' not in frame:
      if not is_pong(frame):
        self.replies.put_nowait(validate_reply(frame))
      return None
    return Subscription(channel=frame['topic'], notification=frame.get('data', frame))


@dataclass(kw_only=True)
class WsEndpoint:
  """Shared validation defaults for a generated Bybit subscribe-shaped WS channel."""

  socket: BybitStreamsClient
  validate: bool = True

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate


class TradeFrame(TypedDict):
  """Any frame Bybit sends on the WS Trade connection: a command reply, or a pong.

  The trade connection's pong shape isn't documented separately from the other
  connections' — see `Frame` — so every field is optional here too, covering both a
  reply's camelCase fields and the general pong shape's snake_case ones. `TradeReply`
  re-validates the stricter reply shape once a frame is confirmed to have a `reqId`.
  """

  reqId: NotRequired[str]
  retCode: NotRequired[int]
  retMsg: NotRequired[str]
  op: NotRequired[str]
  data: NotRequired[Any]
  retExtInfo: NotRequired[Any]
  connId: NotRequired[str]
  ret_msg: NotRequired[str]
  conn_id: NotRequired[str]
  req_id: NotRequired[str]
  args: NotRequired[list]


validate_trade_frame = validator[TradeFrame](TradeFrame)


class TradeReply(TypedDict):
  """Frame Bybit sends in answer to a WS Trade command.

  Field names are camelCase here, unlike `Reply`'s snake_case — Bybit shapes a trade
  reply like its REST envelope (`retCode`/`retMsg`), not like a stream ack.
  """

  reqId: str
  retCode: int
  retMsg: str
  op: str
  data: NotRequired[Any]
  retExtInfo: NotRequired[Any]
  connId: NotRequired[str]


validate_trade_reply = validator[TradeReply](TradeReply)


@dataclass
class BybitTradeClient(Rpc[Any, TradeReply]):
  """The WS Trade (order entry) connection. `reqId`-correlated request/reply, no pushes.

  Does not yet authenticate before sending — `build_request` constructs and signs a
  command frame without needing a live connection, so its shape can be inspected or
  compared before a command is actually sent.
  """

  url: str
  credentials: Credentials | None = field(default=None, kw_only=True, repr=False)
  _pending_pongs: deque[int] = field(default_factory=deque, init=False, repr=False)
  """Ids of in-flight `rpc_request` calls sent as a `ping` command, oldest first.

  Every other WS Trade command's reply echoes the `reqId` `rpc_send` injected, so
  `parse_response` correlates it the normal way. `ping`'s `pong` reply never does —
  live-verified twice (`spec/endpoints/trade/ping`), including once with an explicit
  `reqId` on the request — so there is nothing to correlate it against except arrival
  order, the same way `BybitStreamsClient.command` matches a subscribe/unsubscribe ack
  that carries no id at all. Without this, `parse_response` finds no `reqId` on the
  `pong`, drops it, and the `rpc_request` future backing it is never resolved —
  `typed_core.ws.Socket.wait` applies no timeout of its own (only `force_open` does),
  so the call would hang until the connection itself drops.
  """

  async def ping(self, ws):
    """Periodic keepalive ping, fired by `Socket.pinger` — its `pong` reply is never
    awaited, so it doesn't touch `_pending_pongs`; a `pong` arriving with no ping of
    ours pending is simply dropped in `parse_response`, same as before this fix."""
    await ws.send(dumps({'op': 'ping'}))

  async def rpc_send(self, id: int, req: Any):
    if req.get('op') == 'ping':
      self._pending_pongs.append(id)
    await (await self.ws).send(dumps({**req, 'reqId': str(id)}))

  def parse_response(self, msg: str | bytes) -> Response[TradeReply] | None:
    """Drop pongs and anything else without a `reqId` before validating — except a
    `ping` command's own `pong`, matched by arrival order against `_pending_pongs`
    since Bybit echoes no `reqId` for it (see that field's docstring)."""
    frame = validate_trade_frame(msg)
    if 'reqId' not in frame:
      if is_pong(frame) and self._pending_pongs:
        id = self._pending_pongs.popleft()
        reply = validate_trade_reply({**frame, 'reqId': str(id)})
        return Response(id=id, reply=reply)
      return None
    reply = validate_trade_reply(frame)
    return Response(id=int(reply['reqId']), reply=reply)

  def build_request(self, op: str, args: list) -> dict:
    """Build the frame `rpc_request` would sign and send, without sending it.

    Compare the result byte for byte against a recorded example to check a command's
    wire shape without needing to actually place an order.

    Args:
      op: Command name, for example `order.create`.
      args: Command parameters, as the venue's `args` array.

    Raises:
      AuthError: The client holds no credentials.
    """
    if self.credentials is None:
      raise AuthError(
        f'{op} requires credentials; build the client with '
        '`Bybit.new(api_key=..., api_secret=...)`.'
      )
    timestamp = str(int(time.time() * 1000))
    return {
      'header': {'X-BAPI-TIMESTAMP': timestamp, 'X-BAPI-RECV-WINDOW': '5000'},
      'op': op,
      'args': args,
    }


@dataclass(kw_only=True)
class TradeEndpoint:
  """Shared validation defaults for a generated Bybit WS Trade command."""

  socket: BybitTradeClient
  validate: bool = True

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate


__all__ = [
  'AUTH_EXPIRY_MS',
  'BybitStreamsClient',
  'BybitTradeClient',
  'PING_INTERVAL',
  'Reply',
  'TradeEndpoint',
  'TradeReply',
  'WS_DEDICATED_REGIONS',
  'WsEndpoint',
  'WsUrls',
  'resolve_ws_urls',
]
