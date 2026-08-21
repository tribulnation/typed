"""dYdX indexer candles types and endpoint."""

from typing_extensions import AsyncIterable, Literal, NotRequired, TypedDict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import pydantic

from typed_core.util import Stream, StreamManager
from .core import StreamsMixin, Unsubscribed

Resolution = Literal['1MIN', '5MINS', '15MINS', '30MINS', '1HOUR', '4HOURS', '1DAY']

class Candle(TypedDict):
  """Candle payload."""
  startedAt: datetime
  ticker: str
  resolution: Literal['1MIN', '5MINS', '15MINS', '30MINS', '1HOUR', '4HOURS', '1DAY']
  low: Decimal
  high: Decimal
  open: Decimal
  close: Decimal
  baseTokenVolume: Decimal
  usdVolume: Decimal
  trades: int
  startingOpenInterest: Decimal
  orderbookMidPriceOpen: NotRequired[Decimal | None]
  orderbookMidPriceClose: NotRequired[Decimal | None]

class Notification(TypedDict):
  """Stream notification payload."""
  startedAt: datetime
  ticker: str
  resolution: Literal['1MIN', '5MINS', '15MINS', '30MINS', '1HOUR', '4HOURS', '1DAY']
  low: Decimal
  high: Decimal
  open: Decimal
  close: Decimal
  baseTokenVolume: Decimal
  usdVolume: Decimal
  trades: int
  startingOpenInterest: Decimal
  orderbookMidPriceOpen: NotRequired[Decimal | None]
  orderbookMidPriceClose: NotRequired[Decimal | None]

class Reply(TypedDict):
  """Reply payload."""
  candles: list[Candle]

reply_adapter = pydantic.TypeAdapter(Reply)
notification_adapter = pydantic.TypeAdapter(Notification)

@dataclass
class Candles(StreamsMixin):
  """Candles payload."""
  def candles(
    self,
    market: str,
    *,
    resolution: Resolution,
    validate: bool | None = None,
    batched: bool = True,
  ) -> StreamManager[Notification, Reply, Unsubscribed]:
    """Subscribe to candle updates by market and resolution.
  
    Args:
      market: Market ticker.
      resolution: Candle resolution.
      validate: Override the client response validation default for this call.
      batched: Request batched WebSocket updates.
  
    Returns:
      A typed stream containing the subscription snapshot, update iterator, and unsubscribe callback.
    """
    return self.raw_candles(
      id=f'{market}/{resolution}',
      batched=batched,
      validate=validate,
    )

  def raw_candles(
    self, *, id: str, batched: bool = True, validate: bool | None = None,
  ) -> StreamManager[Notification, Reply, Unsubscribed]:
    """Subscribe to candle updates by raw channel id.
  
    Args:
      id: Market and candle resolution formatted as {market}/{resolution}.
      batched: Reduce incoming messages by batching contents.
      validate: Override the client response validation default for this stream.
  
    Returns:
      A typed stream containing the subscription snapshot, update iterator, and unsubscribe callback.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/websockets#candles)
    """
    return StreamManager(lambda: self._raw_candles_impl(id=id, batched=batched, validate=validate))

  async def _raw_candles_impl(
    self, *, id: str, batched: bool = True, validate: bool | None = None,
  ) -> Stream[Notification, Reply, Unsubscribed]:
    stream = await self.client.subscribe(f'v4_candles:{id}', {'batched': batched})

    async def parsed_stream() -> AsyncIterable[Notification]:
      """Parsed stream."""
      async for msg in stream:
        data = msg['contents']
        msgs: list[Notification] = data if batched else [data]
        for d in msgs:
          yield notification_adapter.validate_python(d) if self.validate(validate) else d

    c = stream.reply['contents']
    reply: Reply = reply_adapter.validate_python(c) if self.validate(validate) else c
    return Stream(reply, parsed_stream(), stream.unsubscribe)
