"""What a dropped or closed WebSocket connection does to the work bound to it.

Everything a drop broke raises `NetworkError`: every stream made on the dead connection
(right away when a consumer is iterating it, otherwise on its next read, after anything
already received), and every request in flight on it. Leaving a stream whose connection
is gone is a silent no-op: no frame, no reconnect, no exception, so an `async with` exit
surfaces the stream's own error. New work after a drop reconnects transparently. After
the owner closes the client, nothing reconnects on its own, and a cancelled task still
ends with `CancelledError`.

Every test runs against a real local `websockets` server that can drop its connections.
"""

from dataclasses import dataclass, field
import asyncio
import gc
import inspect
import json
import warnings

import pytest
import pytest_asyncio
import websockets
from websockets.asyncio.server import Server, ServerConnection, serve

from typed_core.exceptions import BadRequest, NetworkError
from typed_core.ws import Rpc, Socket, Streams, StreamsRpc
from typed_core.ws.rpc import Response
from typed_core.ws.socket import Context
from typed_core.ws.streams import Subscription
from typed_core.ws.streams_rpc import Message

pytestmark = pytest.mark.asyncio

TIMEOUT = 5


@dataclass
class Venue:
  """Local venue: subscribe/unsubscribe/rpc over JSON frames, droppable at will."""

  connections: list[ServerConnection] = field(default_factory=list)
  """Every connection ever accepted, in order."""
  frames: list[dict] = field(default_factory=list)
  """Every frame received, from any connection."""
  subscribed: dict[ServerConnection, set[str]] = field(default_factory=dict)
  """Channels subscribed on each connection."""
  server: Server | None = None

  @property
  def url(self) -> str:
    """The URL clients connect to."""
    assert self.server is not None
    port = next(iter(self.server.sockets)).getsockname()[1]
    return f'ws://127.0.0.1:{port}'

  def ops(self, op: str) -> list[dict]:
    """Received frames of one kind."""
    return [frame for frame in self.frames if frame['op'] == op]

  async def handler(self, ws: ServerConnection):
    """Answer frames the way a typical venue does, including `Not Subscribed` errors."""
    self.connections.append(ws)
    subs = self.subscribed[ws] = set()
    async for raw in ws:
      msg = json.loads(raw)
      self.frames.append(msg)
      channel, id = msg.get('channel'), msg.get('id')
      if msg['op'] == 'subscribe':
        subs.add(channel)
        await ws.send(json.dumps({'type': 'subscribed', 'channel': channel, 'id': id}))
      elif msg['op'] == 'unsubscribe':
        if channel in subs:
          subs.discard(channel)
          reply = {'type': 'unsubscribed', 'channel': channel, 'id': id}
        else:
          reply = {'type': 'error', 'code': 30002, 'channel': channel, 'id': id}
        await ws.send(json.dumps(reply))
      elif msg.get('drop'):
        await ws.close()
        return
      elif not msg.get('hang'):
        await ws.send(json.dumps({'type': 'result', 'id': id, 'result': msg['params']}))

  async def publish(self, channel: str, data: int):
    """Push `data` to every live connection subscribed to `channel`."""
    for ws, subs in self.subscribed.items():
      if channel in subs and ws.state is websockets.State.OPEN:
        await ws.send(json.dumps({'type': 'data', 'channel': channel, 'data': data}))

  async def drop(self):
    """Close every live connection from the server side."""
    for ws in self.connections:
      if ws.state is websockets.State.OPEN:
        await ws.close()


@pytest_asyncio.fixture
async def venue():
  """A running local venue."""
  venue = Venue()
  async with serve(venue.handler, '127.0.0.1', 0) as server:
    venue.server = server
    yield venue


@pytest.fixture(autouse=True)
def no_unawaited_coroutines():
  """Fail any test that leaves a coroutine never awaited."""
  with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    yield
    gc.collect()
  unawaited = [str(w.message) for w in caught if 'never awaited' in str(w.message)]
  assert not unawaited


class NotSubscribed(BadRequest):
  """The venue's `30002 Not Subscribed` error."""


@dataclass
class WireStreams(Streams[int, None, dict, dict]):
  """`Streams` correlating subscribe/unsubscribe acks by channel."""

  pending: dict[str, asyncio.Future[dict]] = field(default_factory=dict, init=False, repr=False)

  async def exchange(self, op: str, channel: str) -> dict:
    """Send one subscribe/unsubscribe frame and await its ack."""
    future = self.pending[channel] = asyncio.get_running_loop().create_future()
    try:
      await (await self.ws).send(json.dumps({'op': op, 'channel': channel}))
      return await future
    finally:
      if self.pending.get(channel) is future:
        del self.pending[channel]

  async def request_subscription(self, channel: str, params=None) -> dict:
    """Subscribe on the wire."""
    return await self.exchange('subscribe', channel)

  async def request_unsubscription(self, channel: str, params=None) -> dict:
    """Unsubscribe on the wire."""
    return await self.exchange('unsubscribe', channel)

  def parse_msg(self, msg: str | bytes) -> Subscription[int] | None:
    """Route data to streams and acks to their pending request."""
    obj = json.loads(msg)
    if obj['type'] == 'data':
      return {'channel': obj['channel'], 'notification': obj['data']}
    future = self.pending.get(obj['channel'])
    if future is not None and not future.done():
      if obj['type'] == 'error':
        future.set_exception(NotSubscribed(obj['code']))
      else:
        future.set_result(obj)


@dataclass
class WireStreamsRpc(StreamsRpc[dict, dict, int, None, dict, dict]):
  """`StreamsRpc` whose subscribe/unsubscribe are id-correlated RPCs."""

  async def rpc_send(self, id: int, req: dict, /):
    """Send one request frame; a `drop` request waits until the connection is gone."""
    ws = await self.ws
    await ws.send(json.dumps({**req, 'id': id}))
    if req.get('drop'):
      await ws.wait_closed()

  async def exchange(self, op: str, channel: str) -> dict:
    """Subscribe/unsubscribe through `rpc_request`, raising on an error reply."""
    reply = await self.rpc_request({'op': op, 'channel': channel})
    if reply['type'] == 'error':
      raise NotSubscribed(reply['code'])
    return reply

  async def request_subscription(self, channel: str, params=None) -> dict:
    """Subscribe on the wire."""
    return await self.exchange('subscribe', channel)

  async def request_unsubscription(self, channel: str, params=None) -> dict:
    """Unsubscribe on the wire."""
    return await self.exchange('unsubscribe', channel)

  def parse_msg(self, msg: str | bytes, /) -> Message[dict, int] | None:
    """Route data to streams and everything else to its request."""
    obj = json.loads(msg)
    if obj['type'] == 'data':
      return {'kind': 'subscription', 'channel': obj['channel'], 'notification': obj['data']}
    return {'kind': 'response', 'id': obj['id'], 'response': obj}


@dataclass
class WireRpc(Rpc[dict, dict]):
  """Plain id-correlated `Rpc`."""

  def parse_response(self, msg: str | bytes) -> Response[dict] | None:
    """Every frame is a reply."""
    obj = json.loads(msg)
    return {'id': obj['id'], 'reply': obj}

  async def rpc_send(self, id: int, req: dict):
    """Send one request frame; a `drop` request waits until the connection is gone."""
    ws = await self.ws
    await ws.send(json.dumps({**req, 'id': id}))
    if req.get('drop'):
      await ws.wait_closed()


STREAMS = [WireStreams, WireStreamsRpc]
RPCS = [WireRpc, WireStreamsRpc]


def current(client: Socket) -> Context:
  """The client's open connection."""
  assert client._ctx_future is not None and client._ctx_future.done()
  return client._ctx_future.result()


async def noticed(ctx: Context):
  """Wait until the client's listener has seen the connection go."""
  await asyncio.wait_for(asyncio.wait([ctx.listener]), TIMEOUT)


async def read(stream) -> int:
  """Read one item, failing instead of hanging."""
  return await asyncio.wait_for(anext(aiter(stream)), TIMEOUT)


# Socket.wait never drops the coroutine it was handed


async def test_wait_closes_its_coroutine_when_connecting_fails(venue: Venue):
  """Regression: a failed connect left the request coroutine never awaited."""
  url = venue.url
  assert venue.server is not None
  venue.server.close()
  await venue.server.wait_closed()
  client = WireStreams(url)

  async def request():
    """Never meant to run: there is no connection to run it on."""

  coro = request()
  with pytest.raises(NetworkError):
    await client.wait(coro)
  assert inspect.getcoroutinestate(coro) == inspect.CORO_CLOSED


@dataclass
class StalledSocket(Socket):
  """`Socket` whose connect never finishes."""

  connecting: asyncio.Event = field(default_factory=asyncio.Event, init=False)

  def on_msg(self, msg: str | bytes):
    """Unused: never connects."""

  async def force_open(self) -> Context:
    """Signal the attempt, then stall forever."""
    self.connecting.set()
    await asyncio.Event().wait()
    raise AssertionError('unreachable')


async def test_wait_closes_its_coroutine_when_cancelled_while_connecting():
  """Regression: cancelling a wait during its connect left the coroutine never awaited."""
  client = StalledSocket('ws://127.0.0.1:1')

  async def request():
    """Never meant to run: the wait is cancelled before it connects."""

  coro = request()
  waiter = asyncio.create_task(client.wait(coro))
  await client.connecting.wait()
  waiter.cancel()
  with pytest.raises(asyncio.CancelledError):
    await waiter
  assert inspect.getcoroutinestate(coro) == inspect.CORO_CLOSED


@dataclass
class FailingSocket(Socket):
  """`Socket` whose connect fails once released."""

  release: asyncio.Event = field(default_factory=asyncio.Event, init=False)

  def on_msg(self, msg: str | bytes):
    """Unused: never connects."""

  async def force_open(self) -> Context:
    """Fail the connect attempt when the test says so."""
    await self.release.wait()
    raise NetworkError('refused')


async def test_a_failed_connect_fails_every_concurrent_opener():
  """Callers waiting on someone else's connect attempt get its error instead of hanging."""
  client = FailingSocket('ws://127.0.0.1:1')
  openers = [asyncio.create_task(client.open()) for _ in range(3)]
  await asyncio.sleep(0)
  client.release.set()
  results = await asyncio.wait_for(asyncio.gather(*openers, return_exceptions=True), TIMEOUT)
  assert all(isinstance(r, NetworkError) for r in results)
  assert client._ctx_future is None


# Streams


@pytest.mark.parametrize('client_class', STREAMS)
async def test_leaving_a_dropped_stream_raises_its_network_error(venue: Venue, client_class):
  """Regression: leaving a dropped stream reconnected to unsubscribe and raised the venue's
  `Not Subscribed` error, masking the stream's `NetworkError`."""
  async with client_class(venue.url) as client:
    with pytest.raises(NetworkError):
      async with client.subscribe('book') as stream:
        await venue.publish('book', 1)
        assert await read(stream) == 1
        await venue.drop()
        await read(stream)
  assert len(venue.connections) == 1
  assert not venue.ops('unsubscribe')
  assert not client.subscriptions


@pytest.mark.parametrize('client_class', STREAMS)
async def test_an_idle_stream_raises_after_a_drop(venue: Venue, client_class):
  """Regression: a stream nobody was reading reconnected on its next read and hung.

  What arrived before the drop is still delivered, then the stream raises.
  """
  async with client_class(venue.url) as client:
    stream = await client.subscribe('book')
    ctx = current(client)
    await venue.publish('book', 1)
    await venue.drop()
    await noticed(ctx)
    assert await read(stream) == 1
    with pytest.raises(NetworkError):
      await read(stream)
  assert len(venue.connections) == 1


@pytest.mark.parametrize('client_class', STREAMS)
async def test_resubscribing_after_an_unnoticed_drop(venue: Venue, client_class):
  """Regression: the dead connection's subscriptions made resubscribing raise
  "Already subscribed". The old stream's cleanup must not touch the new subscription."""
  client = client_class(venue.url)
  old = await client.subscribe('book')
  ctx = current(client)
  await venue.drop()
  await noticed(ctx)
  new = await client.subscribe('book')
  assert len(venue.connections) == 2
  with pytest.raises(NetworkError):
    await read(old)
  assert await old.unsubscribe() is None
  await venue.publish('book', 2)
  assert await read(new) == 2
  await new.unsubscribe()
  assert len(venue.ops('unsubscribe')) == 1
  assert not client.subscriptions
  await client.__aexit__(None, None, None)


@pytest.mark.parametrize('client_class', STREAMS)
async def test_unsubscribing_from_a_dropped_stream_is_a_silent_no_op(venue: Venue, client_class):
  """No frame, no reconnect, no exception, and the local entry is gone."""
  async with client_class(venue.url) as client:
    stream = await client.subscribe('book')
    ctx = current(client)
    await venue.drop()
    await noticed(ctx)
    assert await stream.unsubscribe() is None
    assert not client.subscriptions
  assert len(venue.connections) == 1
  assert not venue.ops('unsubscribe')


@pytest.mark.parametrize('client_class', STREAMS)
async def test_subscribing_after_drops_reconnects(venue: Venue, client_class):
  """New subscriptions after a drop just reconnect, every time."""
  async with client_class(venue.url) as client:
    for attempt in range(1, 4):
      async with client.subscribe('book') as stream:
        await venue.publish('book', attempt)
        assert await read(stream) == attempt
        ctx = current(client)
        await venue.drop()
        await noticed(ctx)
  assert len(venue.connections) == 3


@pytest.mark.parametrize('client_class', STREAMS)
async def test_nothing_reconnects_after_the_owner_closes(venue: Venue, client_class):
  """Streams left over after the owner's exit fail; unsubscribing them sends nothing."""
  async with client_class(venue.url) as client:
    stream = await client.subscribe('book')
  with pytest.raises(NetworkError):
    await read(stream)
  assert await stream.unsubscribe() is None
  assert len(venue.connections) == 1
  assert client._ctx_future is None


@pytest.mark.parametrize('client_class', STREAMS)
@pytest.mark.parametrize('order', ['close_first', 'cancel_first'])
async def test_a_cancelled_consumer_ends_cancelled_when_the_owner_closes(
  venue: Venue, client_class, order
):
  """Regression: a consumer cancelled around the owner's exit reconnected to unsubscribe
  and could end with `NetworkError` or the venue's error instead of `CancelledError`."""
  client = client_class(venue.url)
  ready = asyncio.Event()

  async def consume():
    """Iterate one stream until cancelled."""
    async with client.subscribe('book') as stream:
      ready.set()
      async for _ in stream:
        pass

  task = asyncio.create_task(consume())
  await ready.wait()
  task.cancel()
  if order == 'cancel_first':
    await asyncio.sleep(0)
  await client.__aexit__(None, None, None)
  with pytest.raises(asyncio.CancelledError):
    await asyncio.wait_for(task, TIMEOUT)
  assert len(venue.connections) == 1
  assert client._ctx_future is None


@pytest.mark.parametrize('client_class', STREAMS)
async def test_a_cancelled_consumer_unsubscribes_on_a_live_connection(venue: Venue, client_class):
  """Cancellation on a healthy connection still unsubscribes and ends cancelled."""
  async with client_class(venue.url) as client:
    ready = asyncio.Event()

    async def consume():
      """Iterate one stream until cancelled."""
      async with client.subscribe('book') as stream:
        ready.set()
        async for _ in stream:
          pass

    task = asyncio.create_task(consume())
    await ready.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
      await asyncio.wait_for(task, TIMEOUT)
    assert len(venue.ops('unsubscribe')) == 1
    assert not client.subscriptions


# Requests


@pytest.mark.parametrize('client_class', RPCS)
async def test_an_in_flight_request_raises_and_forgets_its_reply(venue: Venue, client_class):
  """Regression: a request on a dropped connection left its reply future behind."""
  async with client_class(venue.url) as client:
    request = asyncio.create_task(client.rpc_request({'op': 'rpc', 'params': 1, 'hang': True}))
    while not venue.ops('rpc'):
      await asyncio.sleep(0.01)
    await venue.drop()
    with pytest.raises(NetworkError):
      await asyncio.wait_for(request, TIMEOUT)
    assert not client.replies


@pytest.mark.parametrize('client_class', RPCS)
async def test_a_request_stays_on_the_connection_it_was_sent_on(venue: Venue, client_class):
  """Regression: a connection dropping between sending a request and waiting for its reply
  made the wait reconnect and hang on a connection that never saw the request."""
  async with client_class(venue.url) as client:
    with pytest.raises(NetworkError):
      await asyncio.wait_for(client.rpc_request({'op': 'rpc', 'params': 1, 'drop': True}), TIMEOUT)
    assert len(venue.connections) == 1
    assert not client.replies


@pytest.mark.parametrize('client_class', RPCS)
async def test_requesting_after_drops_reconnects(venue: Venue, client_class):
  """New requests after a drop just reconnect, every time."""
  async with client_class(venue.url) as client:
    for attempt in range(1, 4):
      reply = await asyncio.wait_for(client.rpc_request({'op': 'rpc', 'params': attempt}), TIMEOUT)
      assert reply['result'] == attempt
      ctx = current(client)
      await venue.drop()
      await noticed(ctx)
  assert len(venue.connections) == 3


@pytest.mark.parametrize('client_class', RPCS)
async def test_a_request_in_flight_when_the_owner_closes_raises(venue: Venue, client_class):
  """Closing the client fails its in-flight requests with `NetworkError`, not `CancelledError`."""
  client = client_class(venue.url)
  request = asyncio.create_task(client.rpc_request({'op': 'rpc', 'params': 1, 'hang': True}))
  while not venue.ops('rpc'):
    await asyncio.sleep(0.01)
  await client.__aexit__(None, None, None)
  with pytest.raises(NetworkError):
    await asyncio.wait_for(request, TIMEOUT)
  assert not client.replies
  assert len(venue.connections) == 1
