"""Futures' private WebSocket connection: authenticates once (`login`, a one-shot
signed command with no reply-shaped subscribe of its own -- `futures.streams.user.login`,
`surface: handwritten`) and pushes user data automatically afterward (`docs/spec/
authoring.md` rule 11's `after_rpc` shape).
"""

from typing_extensions import Any
from dataclasses import dataclass, field
import asyncio
from datetime import timedelta
import orjson

from typed_core.exceptions import AuthError
from typed_core.ws.streams import Streams, Subscription

from typed_mexc.core.auth import Credentials, sign
from typed_mexc.core.types import timestamp_millis
from .client import validate_reply, Reply, MEXC_FUTURES_SOCKET_URL


@dataclass
class FuturesPrivateStreamsClient(Streams[Any, Any, Reply | None, Reply | None]):
  """The private Futures WebSocket connection. `request_subscription`/
  `request_unsubscription` send no frame of their own -- MEXC pushes every private
  channel automatically once logged in -- they only ensure `login` has completed."""

  credentials: Credentials | None
  """`None` means unauthenticated -- `authenticate()` raises `AuthError` on first use."""
  auth_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  authorized: asyncio.Event = field(default_factory=asyncio.Event, init=False)
  ping_interval: timedelta = field(default=timedelta(seconds=15), kw_only=True)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: asyncio.Queue[Reply] = field(default_factory=asyncio.Queue, init=False)
  url: str = field(default=MEXC_FUTURES_SOCKET_URL, kw_only=True)

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

  @property
  async def authed(self) -> Reply | None:
    """The real `login` confirmation, on the call that actually performs it; `None`
    on every later call once this connection is already authenticated (there is
    nothing new to report -- see `authenticate`)."""
    return await self.authenticate()

  async def authenticate(self) -> Reply | None:
    """Authenticate this connection, idempotently. Returns the real `login` reply
    the first time it runs; returns `None` on every subsequent call, since this
    connection is then already authenticated and no further wire exchange happens."""
    if self.auth_lock.locked() or self.authorized.is_set():
      return None
    async with self.auth_lock:
      reply = await self.login()
      self.authorized.set()
      return reply

  async def login(self) -> Reply:
    """Authenticate this connection (`futures.streams.user.login`'s own
    hand-written implementation).

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    t = timestamp_millis.now()
    signature = sign(f'{self.credentials.api_key}{t}', secret=self.credentials.api_secret)
    r = await self.request('login', {
      'apiKey': self.credentials.api_key,
      'reqTime': t,
      'signature': signature,
    })
    if r['data'] != 'success':
      raise AuthError(f'Failed to log in to Futures private WebSocket: {r}')
    return r

  async def request_subscription(self, channel: str, params=None) -> Reply | None:
    """No subscribe frame of its own -- private futures channels push automatically
    once logged in (module docstring). Returns the real `login` confirmation the
    first time this connection authenticates, `None` on every later subscribe once
    already authenticated."""
    return await self.authed

  async def request_unsubscription(self, channel: str, params=None) -> Reply | None:
    """No unsubscribe frame of its own either -- see `request_subscription`."""
    return await self.authed

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    """`self.subscriptions` is keyed by the endpoint's own declared `spec.channel`
    (`push.personal.order`, ...) verbatim -- private channels never send a subscribe
    frame of their own (`request_subscription` above is a pure auth gate), so there is
    no separate wire-vs-local naming to reconcile the way the public client's
    `parse_msg` has to; the server's own push frame channel already matches the
    subscribed key as-is. The delivered notification is the whole, still-raw
    `{channel, data, ts}` frame (matching every generated push message type's own
    declared shape, design/rule 6), not narrowed to `data` alone -- re-decoded from
    `msg` rather than reusing `r`, whose `ts` field `Reply` already converted to a
    `datetime`, which would double-convert against `response_type`'s own
    `TimestampMillis`-typed `ts` field (see `client.py`'s identical `parse_msg`
    docstring for the full reasoning).
    """
    r = validate_reply(msg)
    if r['channel'].startswith('push.'):
      return {'channel': r['channel'], 'notification': orjson.loads(msg)}
    self.replies.put_nowait(r)
