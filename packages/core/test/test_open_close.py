"""Opening and closing a transport stay correct under cancellation and concurrency.

The owner is whoever entered the transport with `async with`; its exit closes it.

- A caller cancelled while waiting for someone else's connect leaves that connect, and
  the socket, working: the shared connection future is never cancelled on its behalf.
- The owner's exit never waits for a connect in flight, which may be stuck in a
  handshake. That connect closes its own connection once it completes and fails with
  `NetworkError` for the callers that joined it before the exit, so nothing stays open
  after the owner has left. A caller that joined it only after the exit tries once more.
- An exit cancelled mid close handshake aborts the connection instead of leaving it
  half-closed; an `HttpClient` exit cancelled while waiting for its lock still closes.
- Work in flight when the owner closes raises `NetworkError`, and extra exits are harmless.

WebSocket tests run against the real local server from `test_ws_drops.py`; HTTP runs
through `httpx.MockTransport`.
"""

from dataclasses import dataclass
from typing_extensions import Any
import asyncio
import json

import httpx
import pytest
import websockets

from typed_core.exceptions import NetworkError
from typed_core.http import HttpClient
from typed_core.ws import Socket

from test_ws_drops import (
  RPCS, STREAMS, TIMEOUT, Venue, WireRpc,
  current, no_unawaited_coroutines, venue,  # noqa: F401 -- fixtures, found by name
)

pytestmark = pytest.mark.asyncio

SOCKETS = sorted({*STREAMS, *RPCS}, key=lambda cls: cls.__name__)


def live(venue: Venue) -> int:
  """How many of the venue's connections are still open."""
  return sum(ws.state is websockets.State.OPEN for ws in venue.connections)


async def settle():
  """Give background closes and handshakes a moment to run."""
  for _ in range(20):
    await asyncio.sleep(0.01)


@pytest.fixture
def gate(monkeypatch: pytest.MonkeyPatch) -> asyncio.Event:
  """Hold every `websockets.connect` until the returned event is set."""
  gate = asyncio.Event()
  connect = websockets.connect

  async def gated(*args: Any, **kwargs: Any):
    """Connect once the test opens the gate."""
    await gate.wait()
    return await connect(*args, **kwargs)

  monkeypatch.setattr(websockets, 'connect', gated)
  return gate


@pytest.fixture
def mock_http(monkeypatch: pytest.MonkeyPatch):
  """Serve every `HttpClient` request from `httpx.MockTransport`."""
  real = httpx.AsyncClient

  def client(**kwargs: Any) -> httpx.AsyncClient:
    """An `httpx.AsyncClient` answering every request locally."""
    return real(transport=httpx.MockTransport(lambda request: httpx.Response(200)), trust_env=False)

  monkeypatch.setattr(httpx, 'AsyncClient', client)


async def rpc(client: WireRpc, params: int = 1) -> int:
  """Send one request and return its echoed params."""
  reply = await asyncio.wait_for(client.rpc_request({'op': 'rpc', 'params': params}), TIMEOUT)
  return reply['result']


# A cancelled open() waiter


@pytest.mark.parametrize('client_class', SOCKETS)
async def test_a_cancelled_waiter_leaves_the_connect_working(
  venue: Venue, gate: asyncio.Event, client_class: type[Socket]
):
  """Regression: a caller cancelled while waiting on another task's connect cancelled the
  shared connection future, so the connect failed with `InvalidStateError`, its connection
  leaked, and every later `open()` raised `CancelledError`."""
  async with client_class(venue.url) as client:
    opener = asyncio.create_task(client.open())
    await asyncio.sleep(0)
    waiter = asyncio.create_task(client.open())
    await asyncio.sleep(0)
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
      await waiter
    gate.set()
    ctx = await asyncio.wait_for(opener, TIMEOUT)
    assert ctx.alive
    assert await asyncio.wait_for(client.open(), TIMEOUT) is ctx
  assert not ctx.alive
  await settle()
  assert live(venue) == 0
  assert len(venue.connections) == 1


@pytest.mark.parametrize('client_class', RPCS)
async def test_requests_work_after_a_cancelled_waiter(
  venue: Venue, gate: asyncio.Event, client_class
):
  """The socket stays usable, on the one connection, after a waiter is cancelled."""
  async with client_class(venue.url) as client:
    first = asyncio.create_task(rpc(client, 1))
    await asyncio.sleep(0)
    cancelled = asyncio.create_task(rpc(client, 2))
    await asyncio.sleep(0)
    cancelled.cancel()
    await asyncio.gather(cancelled, return_exceptions=True)
    gate.set()
    assert await first == 1
    assert await rpc(client, 3) == 3
  assert len(venue.connections) == 1
  await settle()
  assert live(venue) == 0


# The owner's exit while a connect is in flight


@pytest.mark.parametrize('client_class', SOCKETS)
async def test_an_exit_during_a_connect_closes_what_it_opens(
  venue: Venue, gate: asyncio.Event, client_class: type[Socket]
):
  """Regression: the owner's exit while another task was connecting closed nothing, so the
  connect finished afterwards and left a connection nobody would close. Now the exit
  returns at once, and the connect closes its connection and fails its caller."""
  client = client_class(venue.url)
  async with client:
    opener = asyncio.create_task(client.open())
    await asyncio.sleep(0)
  assert not opener.done()
  gate.set()
  with pytest.raises(NetworkError):
    await asyncio.wait_for(opener, TIMEOUT)
  assert client._ctx_future is None
  await settle()
  assert live(venue) == 0
  assert len(venue.connections) == 1


@pytest.mark.parametrize('client_class', RPCS)
async def test_the_exit_fails_work_that_joined_the_connect_before_it(
  venue: Venue, gate: asyncio.Event, client_class
):
  """A request waiting on a connect that the owner's exit overtook raises `NetworkError`
  instead of hanging, and no frame is sent on the closed connection."""
  client = client_class(venue.url)
  await client.__aenter__()
  request = asyncio.create_task(rpc(client))
  await asyncio.sleep(0)
  await asyncio.wait_for(client.__aexit__(None, None, None), TIMEOUT)
  gate.set()
  with pytest.raises(NetworkError):
    await asyncio.wait_for(request, TIMEOUT)
  assert not venue.ops('rpc')
  await settle()
  assert live(venue) == 0


@pytest.mark.parametrize('client_class', RPCS)
async def test_work_joining_the_connect_after_the_exit_retries(
  venue: Venue, gate: asyncio.Event, client_class
):
  """A caller that started after the owner exited, but joined a connect begun before it,
  doesn't fail with it: it reconnects once and succeeds."""
  client = client_class(venue.url)
  await client.__aenter__()
  before = asyncio.create_task(client.open())
  await asyncio.sleep(0)
  await client.__aexit__(None, None, None)
  async with client:
    after = asyncio.create_task(rpc(client, 2))
    await asyncio.sleep(0)
    gate.set()
    with pytest.raises(NetworkError):
      await asyncio.wait_for(before, TIMEOUT)
    assert await asyncio.wait_for(after, TIMEOUT) == 2
  assert len(venue.connections) == 2
  await settle()
  assert live(venue) == 0


@pytest.mark.parametrize('client_class', RPCS)
async def test_an_exit_while_a_dead_connection_is_closed_reopens_nothing(
  venue: Venue, client_class
):
  """Regression: a caller that found the connection dead closed it, and the owner exiting
  meanwhile saw nothing to close; the caller then reconnected with no owner left."""
  client = client_class(venue.url)
  await client.__aenter__()
  assert await rpc(client) == 1
  ctx = current(client)
  ctx.pinger.cancel()
  await asyncio.sleep(0)
  assert not ctx.alive
  reopening = asyncio.create_task(client.open())
  await asyncio.sleep(0)
  assert client._ctx_future is None and not client.open_lock.locked()
  await client.__aexit__(None, None, None)
  with pytest.raises(NetworkError):
    await asyncio.wait_for(reopening, TIMEOUT)
  assert len(venue.connections) == 1
  await settle()
  assert live(venue) == 0


@pytest.mark.parametrize('client_class', RPCS)
async def test_a_cancelled_exit_during_a_connect_still_closes_it(
  venue: Venue, gate: asyncio.Event, client_class
):
  """Regression: an exit cancelled while it waited for a connect in flight skipped the
  close, so the connect opened with no owner left."""
  client = client_class(venue.url)
  await client.__aenter__()
  opener = asyncio.create_task(client.open())
  await asyncio.sleep(0)
  exiting = asyncio.create_task(client.__aexit__(None, None, None))
  await asyncio.sleep(0)
  exiting.cancel()
  await asyncio.gather(exiting, return_exceptions=True)
  gate.set()
  with pytest.raises(NetworkError):
    await asyncio.wait_for(opener, TIMEOUT)
  await settle()
  assert live(venue) == 0


@dataclass
class HandshakeRpc(WireRpc):
  """`Rpc` whose `force_open` awaits a bootstrap reply with no timeout, as some venues'
  heartbeat setup does."""

  async def force_open(self):
    """Connect, then wait for a handshake reply the venue never sends; a connection whose
    handshake fails or is cancelled is closed here, the only place that can reach it."""
    ctx = await super().force_open()
    try:
      id = self.counter
      self.counter += 1
      self.replies[id] = asyncio.get_running_loop().create_future()
      await ctx.ws.send(json.dumps({'op': 'rpc', 'hang': True, 'params': 0, 'id': id}))
      await self.wait(self.replies[id], ctx=ctx)
      del self.replies[id]
    except BaseException:
      await self.close(ctx)
      raise
    return ctx


async def test_an_exit_never_waits_for_a_stalled_handshake(venue: Venue):
  """Regression: the owner's exit waited for a connect in flight, so a handshake the venue
  never answered hung the exit forever."""
  client = HandshakeRpc(venue.url)
  await client.__aenter__()
  opener = asyncio.create_task(client.open())
  while not venue.ops('rpc'):
    await asyncio.sleep(0.01)
  await asyncio.wait_for(client.__aexit__(None, None, None), 1)
  assert not opener.done()
  opener.cancel()
  await asyncio.gather(opener, return_exceptions=True)
  await settle()
  assert live(venue) == 0


@pytest.mark.parametrize('client_class', SOCKETS)
async def test_an_exit_during_a_failing_connect_is_quiet(
  venue: Venue, gate: asyncio.Event, client_class: type[Socket]
):
  """A connect that fails while the owner exits fails its caller; the exit raises nothing."""
  client = client_class(venue.url)
  assert venue.server is not None
  venue.server.close()
  await venue.server.wait_closed()
  async with client:
    opener = asyncio.create_task(client.open())
    await asyncio.sleep(0)
    gate.set()
  with pytest.raises(NetworkError):
    await opener
  assert client._ctx_future is None


# Cancelled exits


@pytest.mark.parametrize('client_class', RPCS)
async def test_an_exit_cancelled_mid_close_aborts_the_connection(venue: Venue, client_class):
  """Regression: an exit cancelled during the close handshake left the connection half
  closed, with its TCP connection open and nothing left to reach it."""
  client = client_class(venue.url)
  await client.__aenter__()
  assert await rpc(client) == 1
  ws = current(client).ws
  peer = venue.connections[-1].transport
  peer.pause_reading()
  exiting = asyncio.create_task(client.__aexit__(None, None, None))
  await asyncio.sleep(0.05)
  exiting.cancel()
  with pytest.raises(asyncio.CancelledError):
    await exiting
  assert client._ctx_future is None
  assert ws.transport.is_closing()
  peer.resume_reading()
  await settle()
  assert live(venue) == 0


async def test_an_http_exit_cancelled_waiting_for_its_lock_still_closes(mock_http):
  """Regression: an exit cancelled while a request held the lock (opening the client)
  never closed the `httpx.AsyncClient`."""
  client = HttpClient()
  await client.__aenter__()
  await client.request('GET', 'http://venue.test/')
  connection = client._client
  assert connection is not None
  async with client.lock:
    exiting = asyncio.create_task(client.__aexit__(None, None, None))
    await asyncio.sleep(0)
    exiting.cancel()
    with pytest.raises(asyncio.CancelledError):
      await exiting
  await settle()
  assert connection.is_closed
  assert client._client is None


# Work in flight at the owner's exit, and extra exits


@pytest.mark.parametrize('client_class', RPCS)
async def test_the_owners_exit_fails_a_pending_reply(venue: Venue, client_class):
  """A request waiting for its reply when the owner exits raises `NetworkError`."""
  async with client_class(venue.url) as client:
    request = asyncio.create_task(client.rpc_request({'op': 'rpc', 'params': 1, 'hang': True}))
    while not venue.ops('rpc'):
      await asyncio.sleep(0.01)
  with pytest.raises(NetworkError):
    await asyncio.wait_for(request, TIMEOUT)
  assert not client.replies
  assert len(venue.connections) == 1


@pytest.mark.parametrize('client_class', RPCS)
async def test_extra_exits_are_harmless(venue: Venue, client_class):
  """An exit before any use, or after the close, opens nothing and raises nothing; the
  next owner still gets a working socket."""
  client = client_class(venue.url)
  await client.__aexit__(None, None, None)
  async with client:
    assert await rpc(client) == 1
  await client.__aexit__(None, None, None)
  await client.__aexit__(None, None, None)
  assert len(venue.connections) == 1
  async with client:
    assert await rpc(client) == 1
  await settle()
  assert live(venue) == 0
  assert len(venue.connections) == 2


async def test_extra_http_exits_are_harmless(mock_http):
  """The same for `HttpClient`."""
  client = HttpClient()
  await client.__aexit__(None, None, None)
  async with client:
    await client.request('GET', 'http://venue.test/')
    connection = client._client
  assert connection is not None and connection.is_closed
  await client.__aexit__(None, None, None)
  async with client:
    await client.request('GET', 'http://venue.test/')
    assert client._client is not connection
