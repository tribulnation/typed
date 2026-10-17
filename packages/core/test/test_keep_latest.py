"""Keep-latest subscriptions deliver only the newest snapshot and parse only what is read."""

import asyncio
import json
from unittest.mock import Mock

import pytest
import pytest_asyncio
import websockets

from typed_core.ws.socket import Context
from typed_core.ws.streams import Streams, Subscription
from typed_core.ws.streams_rpc import Message, StreamsRpc

pytestmark = pytest.mark.asyncio

PREFIX = '{"stream":"'


def peek(msg: str | bytes) -> str | None:
  """Read a Binance-style combined frame's stream name off its prefix, without decoding it."""
  if isinstance(msg, str) and msg.startswith(PREFIX):
    return msg[len(PREFIX) : msg.index('"', len(PREFIX))]


class CountingStreams(Streams[dict, None, None, None]):
  """Streams over `{"stream": ..., "data": ...}` frames, counting every decode."""

  parsed: int = 0
  raw_routing: bool = True

  async def request_subscription(self, channel: str, params=None):
    """Acknowledge subscription immediately."""

  async def request_unsubscription(self, channel: str, params=None):
    """Acknowledge unsubscribe immediately."""

  def parse_msg(self, msg: str | bytes) -> Subscription[dict]:
    """Decode a combined frame, counting it."""
    self.parsed += 1
    obj = json.loads(msg)
    return {'channel': obj['stream'], 'notification': obj['data']}

  def route_raw(self, msg: str | bytes, /) -> str | None:
    """Route by prefix when enabled."""
    if self.raw_routing:
      return peek(msg)


class CountingStreamsRpc(StreamsRpc[dict, dict, dict, None, None, None]):
  """StreamsRpc over the same frames, plus `{"id": ...}` replies, counting every decode."""

  parsed: int = 0
  raw_routing: bool = True

  async def request_subscription(self, channel: str, params=None):
    """Acknowledge subscription immediately."""

  async def request_unsubscription(self, channel: str, params=None):
    """Acknowledge unsubscribe immediately."""

  async def rpc_send(self, id: int, req: dict, /):
    """No RPC calls are needed for these subscription tests."""

  def parse_msg(self, msg: str | bytes, /) -> Message[dict, dict]:
    """Decode a combined frame or a reply, counting it."""
    self.parsed += 1
    obj = json.loads(msg)
    if 'id' in obj:
      return {'kind': 'response', 'id': obj['id'], 'response': obj}
    else:
      return {'kind': 'subscription', 'channel': obj['stream'], 'notification': obj['data']}

  def route_raw(self, msg: str | bytes, /) -> str | None:
    """Route by prefix when enabled."""
    if self.raw_routing:
      return peek(msg)


async def background():
  """Represent an idle transport task without opening a connection."""
  await asyncio.Event().wait()


@pytest_asyncio.fixture
async def connected():
  """Build clients on an already-open fake connection, cancelling its transport tasks afterwards."""
  transport: list[asyncio.Task] = []

  def connect(client_class, **fields):
    """Attach a fake open connection to a new client."""
    client = client_class(url='wss://example.invalid')
    for name, value in fields.items():
      setattr(client, name, value)
    connection = Mock(spec=websockets.ClientConnection)
    connection.state = websockets.State.OPEN
    listener, pinger = asyncio.create_task(background()), asyncio.create_task(background())
    transport.extend([listener, pinger])
    client.ctx_future.set_result(Context(ws=connection, listener=listener, pinger=pinger))
    return client

  yield connect
  for task in transport:
    task.cancel()
  await asyncio.gather(*transport, return_exceptions=True)


def frame(stream: str, seq: int) -> str:
  """A combined-stream frame carrying a sequence number."""
  return json.dumps({'stream': stream, 'data': {'seq': seq}}, separators=(',', ':'))


client_classes = pytest.mark.parametrize('client_class', [CountingStreams, CountingStreamsRpc])


@client_classes
@pytest.mark.parametrize('raw_routing', [True, False])
async def test_burst_delivers_only_newest_and_counts_skipped(connected, client_class, raw_routing):
  """A burst read late yields its newest message; the rest are counted as skipped."""
  client = connected(client_class, raw_routing=raw_routing)
  stream = await client.subscribe('btc@bookTicker', keep_latest=True)
  for seq in range(100):
    client.on_msg(frame('btc@bookTicker', seq))
  it = aiter(stream)
  assert await anext(it) == {'seq': 99}
  assert stream.skipped == 99
  client.on_msg(frame('btc@bookTicker', 100))
  assert await anext(it) == {'seq': 100}
  assert stream.skipped == 99


@client_classes
async def test_raw_routed_frames_are_parsed_only_when_read(connected, client_class):
  """With raw routing, skipped frames are never decoded: one decode per delivered message."""
  client = connected(client_class)
  stream = await client.subscribe('btc@bookTicker', keep_latest=True)
  for seq in range(1000):
    client.on_msg(frame('btc@bookTicker', seq))
  assert client.parsed == 0
  assert await anext(aiter(stream)) == {'seq': 999}
  assert client.parsed == 1


@client_classes
async def test_waiting_reader_gets_next_message(connected, client_class):
  """A reader already waiting is woken by the next message."""
  client = connected(client_class)
  stream = await client.subscribe('btc@bookTicker', keep_latest=True)
  reader = asyncio.create_task(anext(aiter(stream)))
  await asyncio.sleep(0)
  client.on_msg(frame('btc@bookTicker', 7))
  assert await reader == {'seq': 7}
  assert stream.skipped == 0


@client_classes
async def test_default_mode_is_unchanged(connected, client_class):
  """Without keep_latest every message is parsed on arrival and delivered in order."""
  client = connected(client_class)
  stream = await client.subscribe('btc@trade')
  for seq in range(5):
    client.on_msg(frame('btc@trade', seq))
  assert client.parsed == 5
  it = aiter(stream)
  assert [await anext(it) for _ in range(5)] == [{'seq': seq} for seq in range(5)]
  assert stream.skipped == 0
  assert not client.latest


@client_classes
async def test_modes_mix_on_one_connection(connected, client_class):
  """A keep-latest and an all-messages subscription share a connection independently."""
  client = connected(client_class)
  book = await client.subscribe('btc@bookTicker', keep_latest=True)
  trades = await client.subscribe('btc@trade')
  for seq in range(3):
    client.on_msg(frame('btc@bookTicker', seq))
    client.on_msg(frame('btc@trade', seq))
  assert client.parsed == 3
  it = aiter(trades)
  assert [await anext(it) for _ in range(3)] == [{'seq': seq} for seq in range(3)]
  assert await anext(aiter(book)) == {'seq': 2}
  assert (book.skipped, trades.skipped) == (2, 0)


async def test_rpc_replies_still_route_while_keep_latest(connected):
  """A reply frame is not taken for a notification while raw routing is active."""
  client = connected(CountingStreamsRpc)
  await client.subscribe('btc@bookTicker', keep_latest=True)
  reply = asyncio.get_running_loop().create_future()
  client.replies[3] = reply
  client.on_msg(json.dumps({'id': 3, 'result': None}))
  assert reply.result() == {'id': 3, 'result': None}


@client_classes
async def test_unparseable_frame_fails_the_read_not_the_connection(connected, client_class):
  """A raw-kept frame that fails to parse raises on read, ending that stream only."""
  client = connected(client_class)
  stream = await client.subscribe('btc@bookTicker', keep_latest=True)
  client.on_msg('{"stream":"btc@bookTicker","data":')
  it = aiter(stream)
  with pytest.raises(json.JSONDecodeError):
    await anext(it)
  await stream.unsubscribe()
  stream = await client.subscribe('btc@bookTicker', keep_latest=True)
  client.on_msg(frame('btc@bookTicker', 1))
  assert await anext(aiter(stream)) == {'seq': 1}


@client_classes
async def test_unsubscribe_forgets_keep_latest_slot(connected, client_class):
  """Unsubscribing removes the slot, so later frames are no longer routed to it."""
  client = connected(client_class)
  stream = await client.subscribe('btc@bookTicker', keep_latest=True)
  await stream.unsubscribe()
  assert not client.latest and not client.subscriptions
  client.on_msg(frame('btc@bookTicker', 1))
  assert client.parsed == 1
