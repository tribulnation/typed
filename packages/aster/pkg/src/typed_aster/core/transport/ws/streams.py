"""WebSocket transport for market-data streams: the combined-stream connection
(`wss://<f|s|p>stream.../stream`) of one surface.

`SUBSCRIBE`/`UNSUBSCRIBE` are id-correlated requests answered `{"result": null, "id": n}`
(or `{"id": n, "error": {code, msg}}`); pushes arrive wrapped `{"stream", "data"}` and are
routed by `stream`. The server pings every 5 minutes and `websockets` answers, so no
client ping is needed. Aster acknowledges a subscription to a stream that does not exist
without error; such a subscription simply never pushes.

Stream names are case-sensitive and the server only ever pushes the lowercase-symbol form,
so `SocketStreamClient.subscribe` normalizes each channel with `stream_name` before it is
sent, routed and unsubscribed.
"""

from typing_extensions import Any, TypedDict, TypeVar, cast
from dataclasses import dataclass, field
from datetime import timedelta
import json

from typed_core.exceptions import BadRequest
from typed_core.util import StreamManager
from typed_core.validation import validator
from typed_core.ws import StreamsRpc
from typed_core.ws.streams_rpc import Message

from ...endpoint.stream import StreamClient

T = TypeVar('T')


class StreamAck(TypedDict):
  """A successful `SUBSCRIBE`/`UNSUBSCRIBE` reply."""

  result: None
  id: int


def stream_name(channel: str) -> str:
  """Normalize a stream name to the form Aster pushes: the symbol (the segment before the
  first `@`) lowercased, the rest untouched.

  A subscription to `BTCUSDT@bookTicker` is acknowledged but never pushes. Only the symbol
  is lowercased, since the suffix is case-sensitive (`@kline_1M` is one month, `@kline_1m`
  one minute). An all-market stream (`!bookTicker`) has no symbol and is left as is.
  """
  if channel.startswith('!'):
    return channel
  symbol, sep, rest = channel.partition('@')
  return symbol.lower() + sep + rest


@dataclass
class SocketStream(StreamsRpc[dict, dict, Any, None, StreamAck, StreamAck]):
  """One raw combined-stream connection."""

  async def rpc_send(self, id: int, req: dict, /):
    ws = await self.ws
    await ws.send(json.dumps({**req, 'id': id}))

  def parse_msg(self, msg: str | bytes, /) -> Message[dict, Any] | None:
    obj = json.loads(msg)
    if 'id' in obj:
      return {'kind': 'response', 'id': obj['id'], 'response': obj}
    if 'stream' in obj:
      return {
        'kind': 'subscription',
        'channel': obj['stream'],
        'notification': obj['data'],
      }
    return None

  async def control(self, method: str, channel: str) -> StreamAck:
    """Send one `SUBSCRIBE`/`UNSUBSCRIBE` frame and await its reply.

    Raises:
      BadRequest: The server rejected the frame.
    """
    reply = await self.rpc_request({'method': method, 'params': [channel]})
    if 'error' in reply:
      raise BadRequest(reply['error'])
    return cast(StreamAck, reply)

  async def request_subscription(self, channel: str, params: None = None) -> StreamAck:
    return await self.control('SUBSCRIBE', channel)

  async def request_unsubscription(
    self, channel: str, params: None = None
  ) -> StreamAck:
    return await self.control('UNSUBSCRIBE', channel)


@dataclass(kw_only=True)
class SocketStreamClient(StreamClient):
  """Market-data stream client for one surface, owning its connection and validation."""

  conn: SocketStream
  validate: bool = True

  @classmethod
  def new(
    cls,
    url: str,
    *,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
  ):
    """Build the client for one combined-stream URL."""
    return cls(conn=SocketStream(url=url, timeout=timeout), validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self):
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    manager = self.conn.subscribe(stream_name(channel))
    if validator is None or not self.should_validate(validate):
      return cast(StreamManager[T, Any, Any], manager)
    return manager.map(validator)
