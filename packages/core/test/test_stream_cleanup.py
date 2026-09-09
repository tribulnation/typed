"""Cancellation and unsubscribe must finish every task created by stream reads."""

import asyncio
from unittest.mock import Mock

import pytest
import websockets

from typed_core.ws.socket import Context
from typed_core.ws.streams import Streams
from typed_core.ws.streams_rpc import StreamsRpc

pytestmark = pytest.mark.asyncio


class FakeStreams(Streams[int, None, None, None]):
  """Real stream lifecycle with no wire requests or incoming messages."""

  async def request_subscription(self, channel: str, params=None):
    """Acknowledge subscription immediately."""

  async def request_unsubscription(self, channel: str, params=None):
    """Acknowledge unsubscribe immediately."""

  def parse_msg(self, msg: str | bytes):
    """No wire messages are used by these deterministic tests."""


class FakeStreamsRpc(StreamsRpc[int, int, int, None, None, None]):
  """Real combined RPC/stream lifecycle with no wire requests."""

  async def request_subscription(self, channel: str, params=None):
    """Acknowledge subscription immediately."""

  async def request_unsubscription(self, channel: str, params=None):
    """Acknowledge unsubscribe immediately."""

  async def rpc_send(self, id: int, req: int, /):
    """No RPC calls are needed for these subscription tests."""

  def parse_msg(self, msg: str | bytes, /):
    """No wire messages are used by these deterministic tests."""


async def background():
  """Represent an idle transport task without opening a connection."""
  await asyncio.Event().wait()


def context() -> Context:
  """Build an already-open connection with independently owned transport tasks."""
  connection = Mock(spec=websockets.ClientConnection)
  connection.state = websockets.State.OPEN
  return Context(
    ws=connection,
    listener=asyncio.create_task(background()),
    pinger=asyncio.create_task(background()),
  )


async def cleanup(baseline: set[asyncio.Task]):
  """Clean test-owned tasks even when an assertion reproduces an actual leak."""
  tasks = asyncio.all_tasks() - baseline
  for task in tasks:
    task.cancel()
  await asyncio.gather(*tasks, return_exceptions=True)


@pytest.mark.parametrize('client_class', [FakeStreams, FakeStreamsRpc])
@pytest.mark.parametrize('ending', ['cancel', 'unsubscribe', 'transport_failure'])
async def test_ending_stream_read_finishes_pending_queue_get(
  client_class, ending, monkeypatch
):
  """Every way out of a waiting stream read releases its Queue.get helper task."""
  baseline = asyncio.all_tasks()
  client = client_class(url='wss://example.invalid')
  ctx = context()
  client.ctx_future.set_result(ctx)
  try:
    stream = await client.subscribe('book')
    queue = client.subscriptions['book']
    original_get = queue.get
    started = asyncio.Event()
    getter = None

    async def get():
      """Observe the actual helper task created by the concrete stream primitive."""
      nonlocal getter
      getter = asyncio.current_task()
      started.set()
      return await original_get()

    monkeypatch.setattr(queue, 'get', get)
    before_read = asyncio.all_tasks()
    receiver = asyncio.create_task(anext(aiter(stream)))
    await started.wait()
    if ending == 'cancel':
      receiver.cancel()
      expected = asyncio.CancelledError
    elif ending == 'unsubscribe':
      await stream.unsubscribe()
      expected = StopAsyncIteration
    else:
      ctx.listener.cancel()
      expected = asyncio.CancelledError
    with pytest.raises(expected):
      await receiver
    assert getter is not None and getter.done()
    assert not asyncio.all_tasks() - before_read
    if ending == 'cancel':
      assert not ctx.listener.done() and not ctx.pinger.done()
  finally:
    await cleanup(baseline)


async def test_socket_wait_cancellation_finishes_its_owned_awaitable():
  """Cancelling Socket.wait cancels and joins its request wrapper, not the socket."""
  baseline = asyncio.all_tasks()
  client = FakeStreams(url='wss://example.invalid')
  ctx = context()
  started, finished = asyncio.Event(), asyncio.Event()

  async def request():
    """Represent a blocked request with observable cancellation cleanup."""
    started.set()
    try:
      await asyncio.Event().wait()
    finally:
      finished.set()

  try:
    before_wait = asyncio.all_tasks()
    waiter = asyncio.create_task(client.wait(request(), ctx=ctx))
    await started.wait()
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
      await waiter
    assert finished.is_set()
    assert not asyncio.all_tasks() - before_wait
    assert not ctx.listener.done() and not ctx.pinger.done()
  finally:
    await cleanup(baseline)


@pytest.mark.parametrize('client_class', [FakeStreams, FakeStreamsRpc])
async def test_normal_stream_reads_keep_values_and_unsubscribe_cleanly(client_class):
  """Joining completed helper tasks preserves normal multi-message iteration."""
  baseline = asyncio.all_tasks()
  client = client_class(url='wss://example.invalid')
  ctx = context()
  client.ctx_future.set_result(ctx)
  try:
    stream = await client.subscribe('book')
    before_read = asyncio.all_tasks()
    queue = client.subscriptions['book']
    for value in (1, 2):
      queue.put_nowait(value)
      assert await anext(aiter(stream)) == value
    await stream.unsubscribe()
    with pytest.raises(StopAsyncIteration):
      await anext(aiter(stream))
    assert not asyncio.all_tasks() - before_read
    assert not ctx.listener.done() and not ctx.pinger.done()
  finally:
    await cleanup(baseline)
