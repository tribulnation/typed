"""The `trading_ws` surface: `wss://ws.bit2me.com/v1/trading`, both RPC-shaped (six
one-shot commands) and stream-shaped (public/private channel subscriptions) — see
`spec/core.md`'s Surfaces/WebSocket sections for why this composes `Streams` with
`SerialReplies` rather than `StreamsRpc`.
"""

from dataclasses import dataclass, field
from datetime import timedelta
from typing_extensions import Any, Awaitable, Mapping, Self, TypeVar
import orjson

from typed_core.exceptions import AuthError, BadRequest
from typed_core.util import StreamManager
from typed_core.validation import validator, TypedDict as CoreTypedDict
from typed_core.ws import Streams, SerialReplies
from typed_core.ws.streams import Subscription

from ...auth import Credentials, mint_ws_token
from ...transport.http import BIT2ME_API_URL

BIT2ME_TRADING_WS_URL = 'wss://ws.bit2me.com/v1/trading'
SUBSCRIPTION_SEPARATOR = '|'
"""Separator joining a channel and its symbol into one local subscription key —
Bit2Me lets the same channel run once per symbol (`my-orders` unfiltered and
`my-orders` on `BTC/EUR` are two subscriptions). Neither half can contain the
separator: channels are hyphenated words, symbols are `BASE/QUOTE`."""

T = TypeVar('T')


class Reply(CoreTypedDict):
  """Frame Bit2Me sends in answer to a command or a subscribe/unsubscribe request.

  Only `event` is guaranteed: `authenticate` answers with the event alone, and a
  rejected request answers with `error` in place of `result`/`subscription`.
  """

  event: str


validate_reply = validator(Reply)


def subscription_key(channel: str, symbol: str | None) -> str:
  """The local key identifying one subscription."""
  return f'{channel}{SUBSCRIPTION_SEPARATOR}{symbol or ""}'


@dataclass
class TradingWsConnection(SerialReplies[Reply], Streams[Any, Any, Reply, Reply]):
  """One physical connection. **`data` is not a reliable reply-vs-push discriminator**
  — several command replies carry `data` too (`cancel-order`'s success carries a
  `data: {orderId, status}`, `cancel-all-orders`'s a `data: {userId,
  cancelledOrders}}`, shaped identically to a channel push). The actual
  discriminator is `event`: it's a push only when it names a channel this
  connection is currently subscribed to (by `event`+`symbol`, or `event` alone for
  an unfiltered subscription) — no command's reply `event` (`authenticate`,
  `add-order`, `canceled-order`, `canceled-all-orders`, ..., or the fixed
  `subscribe`/`unsubscribe` ack) ever collides with an actual channel name
  (`order-book`, `my-balance`, ...). Everything else is a reply, matched to
  whichever request is waiting by arrival order under `SerialReplies`'s lock.
  """

  url: str = BIT2ME_TRADING_WS_URL

  async def send(self, msg: object):
    ws = await self.ws
    await ws.send(orjson.dumps(msg))

  def parse_msg(self, msg: str | bytes) -> Subscription[Reply] | None:
    frame = validate_reply(msg)
    key = subscription_key(frame['event'], frame.get('symbol'))
    if key not in self.subscriptions:
      key = subscription_key(frame['event'], None)
    if key not in self.subscriptions:
      self.replies.put_nowait(frame)
      return None
    return {'channel': key, 'notification': frame.get('data', frame)}

  async def request_subscription(self, channel: str, params: Any = None) -> Reply:
    name, _, symbol = channel.partition(SUBSCRIPTION_SEPARATOR)
    msg: dict[str, Any] = {'event': 'subscribe', 'subscription': {'name': name}}
    if symbol:
      msg['symbol'] = symbol
    return await _answered(self.request(msg))

  async def request_unsubscription(self, channel: str, params: Any = None) -> Reply:
    name, _, symbol = channel.partition(SUBSCRIPTION_SEPARATOR)
    msg: dict[str, Any] = {'event': 'unsubscribe', 'subscription': {'name': name}}
    if symbol:
      msg['symbol'] = symbol
    return await _answered(self.request(msg))

  async def command(self, event: str, **params: Any) -> Reply:
    """Send one of the six one-shot commands and wait for its reply."""
    return await _answered(self.request({'event': event, **params}))

  async def authenticate(self, token: str):
    """Log the socket in, so private channels/commands become reachable.

    Raises:
      AuthError: Bit2Me rejects the token.
    """
    reply = await self.request({'event': 'authenticate', 'token': token})
    if (error := reply.get('error')) is not None:
      raise AuthError(error)


async def _answered(pending: Awaitable[Reply]) -> Reply:
  """Raise `BadRequest` on a frame carrying `error`, else pass the reply through."""
  reply = await pending
  if (error := reply.get('error')) is not None:
    raise BadRequest(error)
  return reply


@dataclass(kw_only=True)
class TradingWsClient:
  """Implements `core.endpoint.socket.SocketClient` (both `request()` for the six
  one-shot commands and `subscribe()` for channel subscriptions) over one
  `TradingWsConnection`."""

  conn: TradingWsConnection = field(default_factory=TradingWsConnection)
  credentials: Credentials | None = None
  base_url: str = BIT2ME_API_URL
  """REST base URL the WS auth token is minted from — see `auth.mint_ws_token`."""
  validate: bool = True

  @classmethod
  def new(
    cls,
    *,
    credentials: Credentials | None = None,
    url: str = BIT2ME_TRADING_WS_URL,
    base_url: str = BIT2ME_API_URL,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    ping_interval: timedelta = timedelta(hours=24),
  ) -> Self:
    return cls(
      conn=TradingWsConnection(url=url, timeout=timeout, ping_interval=ping_interval),
      credentials=credentials,
      base_url=base_url,
      validate=validate,
    )

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    await self.conn.__aenter__()
    if self.credentials is not None:
      token = await mint_ws_token(self.credentials, base_url=self.base_url)
      await self.conn.authenticate(token)
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  # SocketClient (typed_bit2me.core.endpoint.socket) -- every `trading_ws` command/
  # channel requires the connection to already be authenticated when private (done
  # once in `__aenter__`), so there is no per-call public/private distinction to make
  # here the way `http`'s `RpcClient.request`/`.authed_request` split has.

  async def request(
    self,
    path: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Send one of the six one-shot commands (`path` names the command's own
    `event`) and wait for its reply. The generated `Request` dict carries its own
    `event` key too (a required, literal-defaulted field on every command's own
    schema) -- dropped here since `path` already is that value and
    `TradingWsConnection.command`'s own `event` positional would otherwise collide
    with it."""
    command_params = {k: v for k, v in (params or {}).items() if k != 'event'}
    reply = await self.conn.command(path, **command_params)
    if validator is not None and self.should_validate(validate):
      return validator.python(reply)
    return reply  # type: ignore[return-value]

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    symbol = (params or {}).get('symbol')
    manager = self.conn.subscribe(subscription_key(channel, symbol))
    if validator is not None and self.should_validate(validate):
      return manager.map(validator.python)
    return manager
