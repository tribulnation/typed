"""dYdX indexer block height types and endpoint."""

from typing_extensions import AsyncIterable, TypedDict
from dataclasses import dataclass
from datetime import datetime
import pydantic

from typed_core.util import Stream, StreamManager
from .core import StreamsMixin, Unsubscribed

class Reply(TypedDict):
  """Reply payload."""
  height: str
  time: datetime

class Notification(TypedDict):
  """Stream notification payload."""
  blockHeight: str
  time: datetime

reply_adapter = pydantic.TypeAdapter(Reply)
notification_adapter = pydantic.TypeAdapter(Notification)

@dataclass
class BlockHeight(StreamsMixin):
  """BlockHeight payload."""
  def block_height(
    self, *, batched: bool = True, validate: bool | None = None
  ) -> StreamManager[Notification, Reply, Unsubscribed]:
    """Subscribe to indexer block height updates.
  
    Args:
      batched: Reduce incoming messages by batching contents.
      validate: Override the client response validation default for this stream.
  
    Returns:
      A typed stream containing the subscription snapshot, update iterator, and unsubscribe callback.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/websockets#block-height)
    """
    return StreamManager(lambda: self._block_height_impl(batched=batched, validate=validate))

  async def _block_height_impl(
    self, *, batched: bool = True, validate: bool | None = None
  ) -> Stream[Notification, Reply, Unsubscribed]:
    stream = await self.client.subscribe('v4_block_height', {'batched': batched})

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

