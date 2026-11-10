"""Push-only feed transports: the per-chain backend's event stream and the pricing stream.

Neither has a subscribe protocol, authentication or a client heartbeat: the server
pushes from the moment the connection opens. A subscription only registers a local
channel; frames for no registered channel are dropped.

- **Backend events**, `wss://backend-{chain}.gains.trade`: `{"name", "value"}` frames,
  routed by `name` (`currentBlock` about four times a second on Arbitrum, `liveEvent`,
  `registerTrade`, ...), each delivering its `value`. One event, `new-trade-history`,
  carries its record beside `name` instead of under `value`
  (`{"name": "new-trade-history", "date", "pair", ...}`): a frame without `value` is
  delivered whole. The full `tradingVariables` payload arrives as one ~3 MB frame
  (2,984,280 bytes measured), re-pushed about once a minute, so the connection accepts
  messages up to `BACKEND_MAX_SIZE` instead of `websockets`' 1 MiB default.
- **Pricing**, `wss://backend-pricing.eu.gains.trade/v3`: JSON arrays. A flat
  `[pairIndex, price, pairIndex, price, ...]` batch is routed to `prices`, a
  one-element `[timestampMs]` heartbeat to `heartbeat`, each delivering the array as
  sent.

A channel whose every frame is a full snapshot (the current block, the gas price, the
whole trading variables, the pricing heartbeat) keeps only the newest unread frame
(`keep_latest`), so a slow consumer of the ~4/s `currentBlock` or of the ~3 MB
`tradingVariables` push never grows a backlog; the stream's `skipped` counts what it
missed. Event channels (trades, open-interest and fee updates, per-address collateral
balances) and the pricing batches (each carries only some pairs) deliver every frame.
"""

from typing_extensions import Any, ClassVar, TypeVar, cast
from abc import abstractmethod
from dataclasses import dataclass, field
import json
import logging

from typed_core.util import StreamManager
from typed_core.validation import validator
from typed_core.ws import Streams
from typed_core.ws.streams import Subscription

from ...endpoint.feed import FeedClient

T = TypeVar('T')

logger = logging.getLogger(__name__)

BACKEND_MAX_SIZE = 16 * 2**20
"""Largest backend event frame accepted, in bytes: the ~3 MB `tradingVariables` push
fits with room to grow, while a runaway frame still closes the connection (1009)."""


@dataclass
class FeedSocket(Streams[Any, None, None, None]):
  """A push-only connection: subscribing and unsubscribing send nothing."""

  snapshot_channels: ClassVar[frozenset[str]] = frozenset()
  """Channels whose every frame is a full snapshot: a subscriber gets only the newest
  frame it has not read yet."""

  async def request_subscription(self, channel: str, params: None = None):
    """Nothing to request: the feed pushes everything."""

  async def request_unsubscription(self, channel: str, params: None = None):
    """Nothing to request: the feed pushes everything."""

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    """Decode a frame and route it, dropping one that is not JSON."""
    try:
      obj = json.loads(msg)
    except ValueError:
      logger.warning('Dropping a non-JSON frame: %.200r', msg)
      return None
    return self.route(obj)

  @abstractmethod
  def route(self, obj: Any) -> Subscription[Any] | None:
    """The local channel and payload of one decoded frame, or `None` to drop it."""


@dataclass
class BackendEventSocket(FeedSocket):
  """The per-chain backend's event stream: `{"name", "value"}` frames, routed by `name`."""

  snapshot_channels: ClassVar[frozenset[str]] = frozenset(
    {'currentBlock', 'currentGas', 'currentL1Block', 'tradingVariables'}
  )
  max_size: int | None = field(kw_only=True, default=BACKEND_MAX_SIZE)
  """Largest incoming frame accepted, in bytes; `None` lifts the limit."""

  def route(self, obj: Any) -> Subscription[Any] | None:
    """Route by event name, delivering the event's `value`, or the whole frame when it
    has none (`new-trade-history` sends its record beside `name`)."""
    if isinstance(obj, dict) and isinstance(obj.get('name'), str):
      return {
        'channel': obj['name'],
        'notification': obj['value'] if 'value' in obj else obj,
      }
    return None


@dataclass
class PricingSocket(FeedSocket):
  """The pricing stream: price batches to `prices`, heartbeats to `heartbeat`."""

  snapshot_channels: ClassVar[frozenset[str]] = frozenset({'heartbeat'})

  def route(self, obj: Any) -> Subscription[Any] | None:
    """Route a one-element array as a heartbeat, any longer one as a price batch; both
    are delivered as sent."""
    if not isinstance(obj, list) or not obj:
      return None
    if len(obj) == 1:
      return {'channel': 'heartbeat', 'notification': obj}
    return {'channel': 'prices', 'notification': obj}


@dataclass(kw_only=True)
class FeedSocketClient(FeedClient):
  """`FeedClient` over one `FeedSocket`, owning frame validation."""

  socket: FeedSocket
  validate: bool = True

  async def __aenter__(self):
    await self.socket.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.socket.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Deliver the frames routed to `channel`, only the newest unread one for a
    snapshot channel; see `FeedClient.subscribe`."""
    manager = self.socket.subscribe(
      channel, keep_latest=channel in self.socket.snapshot_channels
    )
    if validator is None or not (self.validate if validate is None else validate):
      return cast(StreamManager[T, Any, Any], manager)
    return manager.map(validator.python)
