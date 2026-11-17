"""Kraken Futures WebSocket v1: public books and the private account feeds.

One connection carries every feed. Subscriptions are acknowledged by an uncorrelated
`subscribed` event naming the feed (and product), and private feeds carry a signed
challenge obtained once per connection. Protocol-level pings (every 20 s by default)
keep the connection inside the venue's 60 s idle limit.
"""

from dataclasses import dataclass, field
from datetime import timedelta
from decimal import Decimal
from typing_extensions import Any, Literal, NotRequired, TypeVar, cast
import asyncio
import json

from typed_core.exceptions import ApiError, AuthError, BadRequest
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from typed_core.ws import Streams
from typed_core.ws.socket import Context
from typed_core.ws.streams import Subscription

from ..core.types import TimestampMillis
from .auth import FuturesCredentials, sign_challenge

T = TypeVar('T')
Frame = dict[str, Any]
"""A decoded JSON frame."""

FUTURES_WS_URL = 'wss://futures.kraken.com/ws/v1'
DEMO_FUTURES_WS_URL = 'wss://demo-futures.kraken.com/ws/v1'

PrivateFeed = Literal['fills', 'open_orders', 'open_positions', 'balances']
PRIVATE_FEEDS: frozenset[str] = frozenset(
  ('fills', 'open_orders', 'open_orders_verbose', 'open_positions', 'balances')
)
ACK_TIMEOUT = timedelta(seconds=10)
"""How long to wait for a `challenge` or `subscribed` answer."""


class BookLevel(TypedDict):
  """One price level."""

  price: Decimal
  qty: Decimal


class BookSnapshot(TypedDict):
  """The full book of one product, first on every `book` subscription."""

  feed: Literal['book_snapshot']
  product_id: str
  timestamp: TimestampMillis
  seq: int
  bids: list[BookLevel]
  asks: list[BookLevel]
  tickSize: NotRequired[Decimal | None]


class BookUpdate(TypedDict):
  """One level's new size (0 removes it); `seq` increases by one per product."""

  feed: Literal['book']
  product_id: str
  side: Literal['buy', 'sell']
  seq: int
  price: Decimal
  qty: Decimal
  timestamp: TimestampMillis


BookMessage = BookSnapshot | BookUpdate


class WsFill(TypedDict):
  """One own fill."""

  instrument: str
  time: TimestampMillis
  price: Decimal
  seq: int
  buy: bool
  qty: Decimal
  """Contracts, unsigned."""
  remaining_order_qty: NotRequired[Decimal]
  order_id: str
  cli_ord_id: NotRequired[str | None]
  """Only on updates, never in the snapshot."""
  fill_id: str
  fill_type: str
  """`maker`, `taker`, `liquidation`, ..."""
  fee_paid: NotRequired[Decimal | None]
  """Fee in `fee_currency`; negative is a rebate."""
  fee_currency: NotRequired[str | None]
  order_type: NotRequired[str]
  taker_order_type: NotRequired[str]


class FillsMessage(TypedDict):
  """A batch of own fills: the recent ones first (`fills_snapshot`), then new ones."""

  feed: Literal['fills', 'fills_snapshot']
  account: NotRequired[str]
  username: NotRequired[str]
  fills: list[WsFill]


class WsOrder(TypedDict):
  """An open order as the `open_orders` feed carries it."""

  instrument: str
  time: TimestampMillis
  last_update_time: TimestampMillis
  qty: Decimal
  """Remaining (unfilled) contracts."""
  filled: Decimal
  limit_price: Decimal
  stop_price: NotRequired[Decimal | None]
  type: str
  """`limit`, `take_profit`, `stop`."""
  order_id: str
  cli_ord_id: NotRequired[str | None]
  direction: Literal[0, 1]
  """0 buys, 1 sells."""
  reduce_only: bool


class OpenOrdersSnapshot(TypedDict):
  """Every open order, first on subscription."""

  feed: Literal['open_orders_snapshot']
  account: NotRequired[str]
  orders: list[WsOrder]


class OpenOrdersUpdate(TypedDict):
  """An order placed, edited, (partially) filled or gone.

  A gone order (`is_cancel`) may carry only its `order_id`.
  """

  feed: Literal['open_orders']
  order: NotRequired[WsOrder]
  order_id: NotRequired[str]
  is_cancel: bool
  reason: NotRequired[str]


OpenOrdersMessage = OpenOrdersSnapshot | OpenOrdersUpdate


class WsPosition(TypedDict):
  """One open position."""

  instrument: str
  balance: Decimal
  """Signed size in contracts."""
  entry_price: Decimal
  mark_price: NotRequired[Decimal]
  index_price: NotRequired[Decimal]
  pnl: NotRequired[Decimal]
  liquidation_threshold: NotRequired[Decimal | None]
  effective_leverage: NotRequired[Decimal | None]
  initial_margin: NotRequired[Decimal | None]
  maintenance_margin: NotRequired[Decimal | None]


class OpenPositionsMessage(TypedDict):
  """Every open position, on subscription and on each change."""

  feed: Literal['open_positions']
  account: NotRequired[str]
  positions: list[WsPosition]
  seq: NotRequired[int]
  timestamp: NotRequired[TimestampMillis]


class BalancesMessage(TypedDict):
  """Balances and margin of every account; `flex` is the multi-collateral one."""

  feed: Literal['balances', 'balances_snapshot']
  account: NotRequired[str]
  seq: NotRequired[int]
  timestamp: NotRequired[TimestampMillis]
  flex_futures: NotRequired[dict[str, Any]]
  holding: NotRequired[dict[str, Any]]
  futures: NotRequired[dict[str, Any]]


def channel_of(feed: str, product: str | None) -> str:
  """The local channel of a feed: `book:PF_XBTUSD`, or the private feed's name."""
  return f'{feed}:{product}' if product is not None else feed


def raise_alert(message: str):
  """Raise the exception matching an `error`/`alert` event's message."""
  lowered = message.lower()
  if 'auth' in lowered or 'challenge' in lowered or 'api key' in lowered:
    raise AuthError(message)
  if 'invalid' in lowered or 'unknown' in lowered:
    raise BadRequest(message)
  raise ApiError(message)


@dataclass
class FuturesSocket(Streams[Frame, None, Frame, None]):
  """One Futures WebSocket connection and its subscriptions."""

  url: str = FUTURES_WS_URL
  credentials: FuturesCredentials | None = field(default=None, repr=False)
  pending: dict[tuple[str, str | None], asyncio.Future[Frame]] = field(
    default_factory=dict, init=False, repr=False
  )
  """Subscriptions awaiting their `subscribed` event, by feed and product."""
  challenge_reply: asyncio.Future[str] | None = field(
    default=None, init=False, repr=False
  )
  """This connection's signed challenge, once requested."""

  async def send(self, message: Frame):
    """Send one JSON frame on the current connection."""
    ws = await self.ws
    await ws.send(json.dumps(message))

  def connection_closed(self, ctx: Context):
    """Fail what waits on the closed connection and forget its challenge."""
    for future in self.pending.values():
      if not future.done():
        future.set_exception(ApiError('Kraken Futures WebSocket closed'))
        future.exception()
    self.pending.clear()
    if self.challenge_reply is not None and not self.challenge_reply.done():
      self.challenge_reply.cancel()
    self.challenge_reply = None
    super().connection_closed(ctx)

  def fail_pending(self, error: Exception):
    """Fail every pending acknowledgement: the venue's errors are not correlated."""
    for future in (*self.pending.values(), self.challenge_reply):
      if future is not None and not future.done():
        future.set_exception(error)
        future.exception()

  def on_event(self, event: Frame):
    """Resolve the acknowledgement an event answers."""
    match event.get('event'):
      case 'challenge':
        if self.challenge_reply is not None and not self.challenge_reply.done():
          self.challenge_reply.set_result(event['message'])
      case 'subscribed':
        products = event.get('product_ids') or [None]
        for product in products:
          future = self.pending.pop((event['feed'], product), None)
          if future is not None and not future.done():
            future.set_result(event)
      case 'error' | 'alert':
        message = str(event.get('message', event))
        if 'already subscribed' not in message.lower():
          try:
            raise_alert(message)
          except ApiError as e:
            self.fail_pending(e)
      case _:
        pass

  def parse_msg(self, msg: str | bytes) -> Subscription[Frame] | None:
    """Route a feed frame to its channel; handle events on the side."""
    obj = json.loads(msg)
    if 'event' in obj:
      self.on_event(obj)
      return None
    feed = obj.get('feed')
    if feed is None or feed == 'heartbeat':
      return None
    base = feed.removesuffix('_snapshot')
    if base == 'book':
      return Subscription(
        channel=channel_of('book', obj['product_id']), notification=obj
      )
    else:
      return Subscription(channel=base, notification=obj)

  async def challenge(self) -> str:
    """This connection's signed challenge, requested on first use.

    Raises:
      AuthError: The socket has no credentials, or the venue refused the key.
    """
    if self.credentials is None:
      raise AuthError('Private Kraken Futures feeds need credentials')
    if self.challenge_reply is None:
      self.challenge_reply = asyncio.get_running_loop().create_future()
      await self.send({'event': 'challenge', 'api_key': self.credentials.api_key})
    message = await asyncio.wait_for(
      asyncio.shield(self.challenge_reply), ACK_TIMEOUT.total_seconds()
    )
    return message

  async def request_subscription(self, channel: str, params: None = None) -> Frame:
    """Subscribe to a feed and wait for its `subscribed` event."""
    feed, _, product = channel.partition(':')
    message: dict[str, Any] = {'event': 'subscribe', 'feed': feed}
    if product:
      message['product_ids'] = [product]
    if feed in PRIVATE_FEEDS:
      challenge = await self.challenge()
      credentials = cast(FuturesCredentials, self.credentials)
      message |= {
        'api_key': credentials.api_key,
        'original_challenge': challenge,
        'signed_challenge': sign_challenge(challenge, credentials.private_key),
      }
    key = (feed, product or None)
    future = self.pending[key] = asyncio.get_running_loop().create_future()
    await self.send(message)
    try:
      return await asyncio.wait_for(future, ACK_TIMEOUT.total_seconds())
    finally:
      if self.pending.get(key) is future:
        del self.pending[key]

  async def request_unsubscription(self, channel: str, params: None = None) -> None:
    """Unsubscribe from a feed without waiting for the venue's answer."""
    feed, _, product = channel.partition(':')
    message: dict[str, Any] = {'event': 'unsubscribe', 'feed': feed}
    if product:
      message['product_ids'] = [product]
    if feed in PRIVATE_FEEDS and self.credentials is not None:
      challenge = await self.challenge()
      message |= {
        'api_key': self.credentials.api_key,
        'original_challenge': challenge,
        'signed_challenge': sign_challenge(challenge, self.credentials.private_key),
      }
    await self.send(message)


@dataclass(kw_only=True)
class FuturesStreams:
  """Typed subscriptions over one `FuturesSocket`.

  References:
    - [Futures WebSocket](https://docs.kraken.com/api/docs/futures-api/websocket/book)
  """

  socket: FuturesSocket
  validate: bool = True

  def feed(
    self, channel: str, message: type[T], *, validate: bool | None = None
  ) -> StreamManager[T, Frame, None]:
    """Subscribe to `channel`, validating each message as `message`."""
    manager = self.socket.subscribe(channel)
    if not (self.validate if validate is None else validate):
      return cast(StreamManager[T, Frame, None], manager)
    return manager.map(validator(message))

  def book(
    self, product_id: str, *, validate: bool | None = None
  ) -> StreamManager[BookMessage, Frame, None]:
    """One product's book: a `book_snapshot`, then one `book` frame per level change."""
    return self.feed(channel_of('book', product_id), BookMessage, validate=validate)  # type: ignore[arg-type]

  def fills(
    self, *, validate: bool | None = None
  ) -> StreamManager[FillsMessage, Frame, None]:
    """Own fills of every market, with fees: a snapshot of recent ones, then new ones."""
    return self.feed('fills', FillsMessage, validate=validate)

  def open_orders(
    self, *, validate: bool | None = None
  ) -> StreamManager[OpenOrdersMessage, Frame, None]:
    """Open orders of every market: a snapshot, then every change."""
    return self.feed('open_orders', OpenOrdersMessage, validate=validate)  # type: ignore[arg-type]

  def open_positions(
    self, *, validate: bool | None = None
  ) -> StreamManager[OpenPositionsMessage, Frame, None]:
    """Open positions, on subscription and on every change."""
    return self.feed('open_positions', OpenPositionsMessage, validate=validate)

  def balances(
    self, *, validate: bool | None = None
  ) -> StreamManager[BalancesMessage, Frame, None]:
    """Balances and margin, on subscription and on every change."""
    return self.feed('balances', BalancesMessage, validate=validate)
