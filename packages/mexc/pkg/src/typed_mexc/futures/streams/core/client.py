"""Futures' public WebSocket connection: unauthenticated, plain-JSON market pushes
(`{channel, data, ts}`)."""

from typing_extensions import Any, TypedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import orjson

from typed_core.ws.streams import Streams, Subscription
from typed_core.validation import validator

MEXC_FUTURES_SOCKET_URL = 'wss://contract.mexc.com/edge'


class Reply(TypedDict):
  """A push or command-reply frame -- futures wraps both the same way."""

  channel: str
  data: Any
  ts: datetime


validate_reply = validator(Reply)


@dataclass
class FuturesPublicStreamsClient(Streams[Any, Any, Reply, Reply]):
  """One physical Futures WebSocket connection. Every subscribe/unsubscribe command
  is answered `{channel: "rs.sub...."/"rs.unsub...."}`, and every push arrives as
  `{channel: "push.<name>", data, ts}` -- `parse_msg` tells the two apart by the
  `push.` prefix."""

  url: str = field(default=MEXC_FUTURES_SOCKET_URL, kw_only=True)
  ping_interval: timedelta = field(default=timedelta(seconds=15), kw_only=True)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: asyncio.Queue[Reply] = field(default_factory=asyncio.Queue, init=False)

  async def send(self, msg):
    await (await self.ws).send(orjson.dumps(msg), text=True)

  async def send_request(self, method: str, params=None):
    msg = {'method': method}
    if params:
      msg['param'] = params
    await self.send(msg)

  async def request(self, method: str, params=None):
    async with self.lock:
      await self.send_request(method, params)
      return await self.replies.get()

  async def ping(self, ws):
    await ws.send(orjson.dumps({'method': 'ping'}), text=True)

  async def request_subscription(self, channel: str, params=None) -> Reply:
    """`channel` is the endpoint's own declared `spec.channel`, already carrying its
    real wire prefix (`sub.depth.full`, design §8: "channel renders as a plain
    `repr()` of the template string") -- sent as-is, not re-prefixed. A real, caught-
    live bug otherwise: the old hand-rolled backend passed a *bare* channel here and
    added `sub.` itself; the new one already gets the prefixed form, so adding it
    again silently sent `sub.sub.depth.full`.
    """
    return await self.request(channel, params)

  async def request_unsubscription(self, channel: str, params=None) -> Reply:
    return await self.request('unsub.' + channel.removeprefix('sub.'), params)

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    """Match a push frame back to the *subscribed* channel key -- `self.subscriptions`
    is keyed by the full `sub.<name>` string passed to `.subscribe()` (see
    `request_subscription`'s own docstring above), never the bare `<name>` a push
    frame's own `channel` field carries (always `push.<name>`, MEXC's convention
    regardless of which `sub.`-prefixed channel triggered it). The delivered
    notification is the *whole*, still-raw `{channel, data, ts}` frame, matching every
    generated push message type's own declared shape (design/rule 6: schemas describe
    what the core returns) -- not narrowed to `data` alone, so `channel`/`ts` stay
    available to a caller alongside it. Deliberately re-decoded from `msg` rather than
    reusing `r` (below): `r` is validated through `Reply`'s own `ts: datetime` field,
    and hand-written that value straight back through `response_type`'s own
    `TimestampMillis`-typed `ts` field (which expects the raw wire epoch, not an
    already-converted `datetime`) would double-convert and raise.
    """
    r = validate_reply(msg)
    if r['channel'].startswith('push.'):
      raw = orjson.loads(msg)
      bare = r['channel'].removeprefix('push.')
      channel = f'sub.{bare}'
      if bare == 'depth' and channel not in self.subscriptions and 'sub.depth.full' in self.subscriptions:
        # `push.depth` is shared by both `depth` (incremental) and `depth.full` (full
        # snapshot) subscriptions -- MEXC's own wire convention, not a spec ambiguity.
        channel = 'sub.depth.full'
      return {'channel': channel, 'notification': raw}
    self.replies.put_nowait(r)
