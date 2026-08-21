"""dYdX indexer orders types and endpoint."""

from typing_extensions import Any, AsyncIterable, NotRequired, TypedDict, NamedTuple
from dataclasses import dataclass
from decimal import Decimal
import pydantic

from typed_core.util import Stream, StreamManager
from .core import StreamsMixin, Unsubscribed

class BookEntry(TypedDict):
  """BookEntry payload."""
  price: Decimal
  size: Decimal

class NotificationEntry(NamedTuple):
  """NotificationEntry payload."""
  price: Decimal
  size: Decimal

class Notification(TypedDict):
  """Stream notification payload."""
  bids: NotRequired[list[NotificationEntry]]
  asks: NotRequired[list[NotificationEntry]]

class Reply(TypedDict):
  """Reply payload."""
  bids: list[BookEntry]
  asks: list[BookEntry]

reply_adapter = pydantic.TypeAdapter(Reply)
notification_adapter = pydantic.TypeAdapter(Notification)

@dataclass
class Orders(StreamsMixin):
  """Orders payload."""
  def orders(
    self, *, id: str, batched: bool = True, validate: bool | None = None,
  ) -> StreamManager[Notification, Reply, Unsubscribed]:
    """Subscribe to order book updates for a market.
  
    Args:
      id: Market ticker.
      batched: Reduce incoming messages by batching contents.
      validate: Override the client response validation default for this stream.
  
    Returns:
      A typed stream containing the subscription snapshot, update iterator, and unsubscribe callback.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/websockets#orders)
    """
    return StreamManager(lambda: self._orders_impl(id=id, batched=batched, validate=validate))

  async def _orders_impl(
    self, *, id: str, batched: bool = True, validate: bool | None = None,
  ) -> Stream[Notification, Reply, Unsubscribed]:
    stream = await self.client.subscribe(f'v4_orderbook:{id}', {'batched': batched})

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
