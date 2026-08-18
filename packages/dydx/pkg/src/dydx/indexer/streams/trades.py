"""dYdX indexer trades types and endpoint."""

from typing_extensions import AsyncIterable, Literal, TypedDict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import pydantic

from typed_core.util import Stream, StreamManager
from .core import StreamsMixin, Unsubscribed

class Trade(TypedDict):
  """Trade payload."""
  id: str
  side: Literal['BUY', 'SELL']
  size: Decimal
  price: Decimal
  type: Literal['LIMIT', 'LIQUIDATED', 'DELEVERAGED']
  createdAt: datetime
  createdAtHeight: str

class TradeUpdate(TypedDict):
  """TradeUpdate payload."""
  id: str
  createdAt: datetime
  side: Literal['BUY', 'SELL']
  price: Decimal
  size: Decimal
  type: Literal['LIMIT', 'LIQUIDATED', 'DELEVERAGED']

class Reply(TypedDict):
  """Reply payload."""
  trades: list[Trade]

class Notification(TypedDict):
  """Stream notification payload."""
  trades: list[TradeUpdate]

reply_adapter = pydantic.TypeAdapter(Reply)
notification_adapter = pydantic.TypeAdapter(Notification)

@dataclass
class Trades(StreamsMixin):
  """Trades payload."""
  def trades(
    self, *, id: str, batched: bool = True, validate: bool | None = None,
  ) -> StreamManager[Notification, Reply, Unsubscribed]:
    """Subscribe to trade updates for a market.
  
    Args:
      id: Market ticker.
      batched: Reduce incoming messages by batching contents.
      validate: Override the client response validation default for this stream.
  
    Returns:
      A typed stream containing the subscription snapshot, update iterator, and unsubscribe callback.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/websockets#trades)
    """
    return StreamManager(lambda: self._trades_impl(id=id, batched=batched, validate=validate))

  async def _trades_impl(
    self, *, id: str, batched: bool = True, validate: bool | None = None,
  ) -> Stream[Notification, Reply, Unsubscribed]:
    stream = await self.client.subscribe(f'v4_trades:{id}', {'batched': batched})

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
