"""WS Streams transport: Binance's combined market/user-data push connection.

`SUBSCRIBE`/`UNSUBSCRIBE` are ordinary id-correlated requests; market-data pushes carry
no `id`, keyed instead by the combined envelope's `"stream"` field — the mixed
request/reply-plus-push shape `typed_core.ws.StreamsRpc` models directly, unlike the
generic `references/transport/ws.py` pattern (`Streams` + `SerialReplies`), which is for a
venue whose replies carry *no* correlation id at all. Binance always echoes one.
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

BINANCE_STREAM_URL = 'wss://stream.binance.com:9443/stream'

STREAM_PREFIX = '{"stream":"'
"""How every combined-stream push starts on the wire: `{"stream":"<name>","data":{...}}`,
compact, `stream` first (checked against live `stream`/`fstream` frames)."""


class StreamAck(TypedDict):
  """Combined-stream `SUBSCRIBE`/`UNSUBSCRIBE` reply on success — confirmed against every
  captured example, always exactly these two keys, `result` always `null`. An error reply
  (a `code`/`msg` pair instead) raises `BadRequest` before this type is ever returned.
  """
  result: None
  id: int


@dataclass
class SocketStream(StreamsRpc[dict, dict, Any, None, StreamAck, StreamAck]):
  """Raw combined-stream connection: id-correlated `SUBSCRIBE`/`UNSUBSCRIBE`, keyed
  pushes. No `ping()` override needed — Binance pings the client every 20s and the
  `websockets` library answers automatically; Binance never requires the client to ping
  first.
  """

  url: str = BINANCE_STREAM_URL

  async def rpc_send(self, id: int, req: dict):
    ws = await self.ws
    await ws.send(json.dumps({**req, 'id': id}))

  def route_raw(self, msg: str | bytes, /) -> str | None:
    """Read a push's stream name off its exact wire prefix, without decoding the frame.

    Only a text frame starting with `STREAM_PREFIX` and a name free of escapes is routed
    raw; anything else (a reply, another shape) falls back to `parse_msg`.
    """
    if isinstance(msg, str) and msg.startswith(STREAM_PREFIX):
      end = msg.find('"', len(STREAM_PREFIX))
      if end != -1 and '\\' not in (name := msg[len(STREAM_PREFIX) : end]):
        return name

  def parse_msg(self, msg: str | bytes) -> Message[dict, Any] | None:
    obj = json.loads(msg)
    if 'id' in obj:
      return {'kind': 'response', 'id': obj['id'], 'response': obj}
    return {
      'kind': 'subscription',
      'channel': obj['stream'],
      'notification': obj['data'],
    }

  async def request_subscription(self, channel: str, params: None = None) -> StreamAck:
    reply = await self.rpc_request({'method': 'SUBSCRIBE', 'params': [channel]})
    if 'code' in reply:
      raise BadRequest(reply)
    return cast(StreamAck, reply)

  async def request_unsubscription(self, channel: str, params: None = None) -> StreamAck:
    reply = await self.rpc_request({'method': 'UNSUBSCRIBE', 'params': [channel]})
    if 'code' in reply:
      raise BadRequest(reply)
    return cast(StreamAck, reply)


@dataclass(kw_only=True)
class SocketStreamClient(StreamClient):
  """WS Streams client, owning the one combined connection and validation."""

  conn: SocketStream = field(default_factory=SocketStream)
  validate: bool = True

  @classmethod
  def new(
    cls,
    url: str = BINANCE_STREAM_URL,
    *,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
  ):
    """Build one subtree. Thin: no environment lookup — the root's `.new()` owns that,
    see `main.py`.
    """
    return cls(conn=SocketStream(url=url, timeout=timeout), validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
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
    keep_latest: bool = False,
  ) -> StreamManager[T, Any, Any]:
    manager = self.conn.subscribe(channel, keep_latest=keep_latest)
    if validator is None or not self.should_validate(validate):
      return cast(StreamManager[T, Any, Any], manager)
    return manager.map(validator)
