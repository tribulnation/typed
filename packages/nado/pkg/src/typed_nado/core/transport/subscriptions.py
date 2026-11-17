"""Subscriptions WebSocket: `subscribe`/`unsubscribe`/`authenticate` commands, correlated by
`id`, and the events pushed for each stream.

Commands are `{"method", "stream"?, "id", ...}` and answered `{"result", "error"?, "id"}`.
Events are bare objects tagged by `type` (the stream type) and carry no subscription id, so
an event is routed to every subscription whose stream it matches (`matches`): a stream
subscribed for every product (`product_id` omitted) and one for a single product both get
that product's events.
"""

from typing_extensions import Any, Mapping, TypedDict, TypeVar, cast
from dataclasses import dataclass, field
from datetime import timedelta
from functools import lru_cache
import asyncio
import json
import logging

from typed_core.util import StreamManager
from typed_core.validation import validator
from typed_core.ws import StreamsRpc
from typed_core.ws.socket import Context
from typed_core.ws.streams_rpc import Message

from ..endpoint.stream import StreamClient
from ..exc import AuthError, BadRequest, NetworkError, RateLimited
from ..endpoint.wire import SubaccountField
from ..signing import Signer, with_default_subaccount

T = TypeVar('T')

logger = logging.getLogger(__name__)

Event = dict[str, Any]
"""One pushed event, tagged by `type`."""
Reply = dict[str, Any]
"""One command reply: `{"result", "error"?, "id"}`."""


class SubscribeParams(TypedDict):
  """What one subscription sends, and whether its connection must be authenticated."""

  stream: dict[str, Any]
  """The stream object: `type` plus scope."""
  authenticate: bool
  """Authenticate the connection before subscribing."""


def channel_key(stream: Mapping[str, Any]) -> str:
  """The local routing key of a stream: its canonical JSON."""
  return json.dumps(stream, sort_keys=True, separators=(',', ':'))


@lru_cache(maxsize=1024)
def stream_of(channel: str) -> dict[str, Any]:
  """The stream object behind a routing key."""
  return json.loads(channel)


def matches(stream: Mapping[str, Any], event: Mapping[str, Any]) -> bool:
  """Whether `event` belongs to `stream`: same `type`, and every scope value the stream sets
  equal to the event's. A `product_id` scope also matches a `product_ids` list (spread
  liquidations). A scope field the event does not carry cannot tell subscriptions apart and
  matches: `order_update` events carry no `subaccount`, so two `order_update` subscriptions
  for different subaccounts on one connection both receive each other's events.
  """
  if stream.get('type') != event.get('type'):
    return False
  for key, value in stream.items():
    if key == 'type' or value is None:
      continue
    if key in event:
      if event[key] != value:
        return False
    elif key == 'product_id' and isinstance(event.get('product_ids'), list):
      if value not in event['product_ids']:
        return False
  return True


@dataclass
class SubscriptionsSocket(StreamsRpc[Reply, Reply, Event, SubscribeParams, None, None]):
  """One subscriptions connection.

  The server needs a ping frame at least every 30 s and `permessage-deflate`; `websockets`
  provides both by default (a keepalive ping every 20 s, compression negotiated).
  """

  signer: Signer | None = field(default=None, kw_only=True, repr=False)
  """Signs the `authenticate` command; `None` for a public client."""
  reply_timeout: timedelta = field(kw_only=True, default=timedelta(seconds=10))
  """Longest wait for one command reply."""
  authenticated: Context | None = field(default=None, init=False, repr=False)
  """The connection already authenticated, if any: authentication lasts a connection."""
  auth_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  """Keeps two subscriptions from authenticating one connection twice."""

  async def rpc_send(self, id: int, req: Reply, /):
    """Write one command, tagged with its `id`."""
    ws = await self.ws
    await ws.send(json.dumps({**req, 'id': id}))

  def parse_msg(self, msg: str | bytes, /) -> Message[Reply, Event] | None:
    """Tell an event (it has a `type`) from a command reply (an `id`, and a `result` or an
    `error`). Anything else is logged and dropped rather than failing the connection."""
    try:
      obj = json.loads(msg)
    except ValueError:
      logger.warning('Dropping a non-JSON subscriptions frame: %.200r', msg)
      return None
    if not isinstance(obj, dict):
      return None
    if isinstance(obj.get('type'), str):
      return {'kind': 'subscription', 'channel': obj['type'], 'notification': obj}
    if isinstance(obj.get('id'), int) and ('result' in obj or 'error' in obj):
      return {'kind': 'response', 'id': obj['id'], 'response': obj}
    logger.warning('Dropping an unrecognized subscriptions frame: %.200r', msg)
    return None

  def on_msg(self, msg: str | bytes):
    """Resolve a reply, or fan an event out to every subscription it matches."""
    res = self.parse_msg(msg)
    if res is None:
      return
    if res['kind'] == 'response':
      reply = self.replies.get(res['id'])
      if reply is not None and not reply.done():
        reply.set_result(res['response'])
      return
    event = res['notification']
    for channel, queue in list(self.subscriptions.items()):
      if matches(stream_of(channel), event):
        queue.put_nowait(event)

  def connection_closed(self, ctx: Context):
    """Forget that the closed connection was authenticated."""
    if self.authenticated is ctx:
      self.authenticated = None
    super().connection_closed(ctx)

  async def command(self, request: Reply) -> Reply:
    """Send one command and return its reply.

    Raises:
      RateLimited: The reply's `error` reports a rate limit.
      BadRequest: The reply carries any other `error`.
      NetworkError: No reply within `reply_timeout`, or the connection dropped.
    """
    try:
      reply = await asyncio.wait_for(
        self.rpc_request(request), self.reply_timeout.total_seconds()
      )
    except asyncio.TimeoutError:
      raise NetworkError(
        f'No reply to {request.get("method")!r} within the timeout'
      ) from None
    error = reply.get('error')
    if error:
      if 'rate limit' in str(error).lower():
        raise RateLimited(error, reply)
      raise BadRequest(error, reply)
    return reply

  async def ensure_authenticated(self):
    """Authenticate this connection once, signing a `StreamAuthentication`.

    Raises:
      AuthError: The client has no signing key, or the venue refused the signature.
    """
    ctx = await self.ctx
    async with self.auth_lock:
      if self.authenticated is ctx:
        return
      if self.signer is None:
        raise AuthError(
          'Authenticated streams need a signing key; this client was built with `public=True`.'
        )
      tx, signature, _ = self.signer.sign(
        'StreamAuthentication', self.signer.with_defaults('StreamAuthentication', {})
      )
      try:
        await self.command({'method': 'authenticate', 'tx': tx, 'signature': signature})
      except BadRequest as error:
        raise AuthError(*error.args) from error
      self.authenticated = ctx

  async def request_subscription(
    self, channel: str, params: SubscribeParams | None = None
  ):
    """Subscribe to one stream, authenticating the connection first if it must be."""
    if params is None:
      params = {'stream': stream_of(channel), 'authenticate': False}
    if params['authenticate']:
      await self.ensure_authenticated()
    await self.command({'method': 'subscribe', 'stream': params['stream']})

  async def request_unsubscription(
    self, channel: str, params: SubscribeParams | None = None
  ):
    """Unsubscribe from one stream."""
    stream = params['stream'] if params is not None else stream_of(channel)
    await self.command({'method': 'unsubscribe', 'stream': stream})


@dataclass(kw_only=True)
class SubscriptionsTransport(StreamClient):
  """The subscriptions WebSocket, as the stream endpoints use it."""

  socket: SubscriptionsSocket
  """The one subscriptions connection every stream shares."""
  validate: bool = True
  """Validate events by default."""

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  def subscribe(
    self,
    stream: Mapping[str, Any],
    *,
    authenticate: bool = False,
    default_subaccount: SubaccountField | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, None, None]':
    """Subscribe to one stream; see `StreamClient.subscribe`.

    Raises:
      AuthError: The stream needs a subaccount, none was passed, and the client has none
        (`public=True`).
    """
    values = with_default_subaccount(
      str(stream.get('type')), stream, default_subaccount, self.socket.signer
    )
    manager = self.socket.subscribe(
      channel_key(values), {'stream': values, 'authenticate': authenticate}
    )
    if validator is None or not self.should_validate(validate):
      return cast('StreamManager[T, None, None]', manager)
    return manager.map(validator)
