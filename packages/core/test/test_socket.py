"""
Pin `Socket`'s lazy connection contract.

`docs/production_guidelines.md`'s "Core And Instantiation" promises that entering a
client opens nothing, first use of a transport opens exactly that transport, and exiting
closes exactly what was opened -- closing nothing when nothing was. `Socket.__aenter__`
used to call `await self.open()` unconditionally, and `Socket.__aexit__` closed via
`await self.ctx`, whose property falls through to `open()` -- so exiting a socket that
was never entered-and-used dialled out just to hang up. Both are fixed by making
`__aenter__` a no-op and `__aexit__` a guard on `ctx_future.done()`.

These tests run against a `Socket` subclass whose `force_open` is a call-recorder, never a
real `websockets.connect`. The regression test for the finding above uses a subclass whose
`force_open` raises, so any code path that still reaches it fails loudly instead of quietly
opening a socket.
"""
from dataclasses import dataclass, field
from typing_extensions import cast
import asyncio
import pytest
import websockets

from typed_core.ws.socket import Socket, Context

class FakeConnection:
  """Stand-in for `websockets.ClientConnection`: enough surface for `Socket` to treat it as open and closeable."""
  def __init__(self):
    self.state = websockets.State.OPEN
    self.exit_calls: list[tuple] = []

  async def __aexit__(self, exc_type, exc_value, traceback):
    self.exit_calls.append((exc_type, exc_value, traceback))

async def _hang():
  """Background task body that only ever ends via cancellation, standing in for the real listener/pinger tasks."""
  await asyncio.Event().wait()

@dataclass
class RecordingSocket(Socket):
  """`Socket` whose transport is a call-recorder instead of a real connection."""
  open_calls: int = field(default=0, init=False)
  last_connection: FakeConnection | None = field(default=None, init=False)

  def on_msg(self, msg: str | bytes):
    """Unused: no test here drives real message dispatch."""

  async def force_open(self) -> Context:
    """Record the call and hand back a fake connection instead of dialling out."""
    self.open_calls += 1
    self.last_connection = FakeConnection()
    return Context(
      ws=cast(websockets.ClientConnection, self.last_connection),
      listener=asyncio.create_task(_hang()),
      pinger=asyncio.create_task(_hang()),
    )

@dataclass
class RaisingSocket(Socket):
  """`Socket` whose `force_open` raises, to prove a code path never dials out."""

  def on_msg(self, msg: str | bytes):
    """Unused: this socket never reaches message dispatch."""

  async def force_open(self) -> Context:
    """Fail loudly if anything ever tries to open this socket."""
    raise AssertionError('force_open must not be called')

@pytest.mark.asyncio
async def test_aenter_opens_nothing():
  """Entering a socket must not connect."""
  socket = RecordingSocket(url='wss://example.invalid')
  async with socket as opened:
    assert opened is socket
    assert socket.open_calls == 0
    assert not socket.ctx_future.done()

@pytest.mark.asyncio
async def test_aexit_without_use_connects_nothing():
  """Regression test: exiting a socket that was never used must not open one just to close it.

  Before the fix, `__aexit__` read `await self.ctx`, whose property falls through to
  `open()`. Using a `force_open` that raises turns "it dialled out" into a hard failure
  instead of a silent one.
  """
  async with RaisingSocket(url='wss://example.invalid'):
    pass

@pytest.mark.asyncio
async def test_use_opens_the_socket():
  """First use of the socket opens it exactly once."""
  socket = RecordingSocket(url='wss://example.invalid')
  async with socket:
    ctx = await socket.open()
  assert socket.open_calls == 1
  assert ctx.ws is socket.last_connection

@pytest.mark.asyncio
async def test_two_touches_open_once():
  """Two uses of the socket within one `async with` open the transport once, not twice."""
  socket = RecordingSocket(url='wss://example.invalid')
  async with socket:
    await socket.open()
    await socket.open()
  assert socket.open_calls == 1

@pytest.mark.asyncio
async def test_aexit_closes_what_was_opened():
  """Exiting after use closes exactly the connection that was opened."""
  socket = RecordingSocket(url='wss://example.invalid')
  async with socket:
    await socket.open()
  connection = socket.last_connection
  assert connection is not None
  assert len(connection.exit_calls) == 1

@pytest.mark.asyncio
async def test_exception_in_body_still_closes_what_was_opened():
  """An exception raised inside the `async with` body must not skip closing an opened socket."""
  socket = RecordingSocket(url='wss://example.invalid')
  with pytest.raises(RuntimeError, match='boom'):
    async with socket:
      await socket.open()
      raise RuntimeError('boom')
  connection = socket.last_connection
  assert connection is not None
  assert len(connection.exit_calls) == 1
  exc_type, exc_value, _ = connection.exit_calls[0]
  assert exc_type is RuntimeError
  assert str(exc_value) == 'boom'

@pytest.mark.asyncio
async def test_reentering_after_exit_gets_a_working_connection():
  """A socket entered, used, exited and re-entered opens a fresh connection, not a consumed future."""
  socket = RecordingSocket(url='wss://example.invalid')
  async with socket:
    await socket.open()
  first_connection = socket.last_connection
  async with socket:
    ctx = await socket.open()
  assert socket.open_calls == 2
  assert first_connection is not None
  assert first_connection.exit_calls
  assert ctx.ws is socket.last_connection
  assert ctx.ws is not first_connection

def test_a_socket_is_constructible_outside_an_event_loop():
  """Building a socket must not need a running loop; connecting is what needs one.

  `ctx_future` used to be a `default_factory=asyncio.Future`, and `asyncio.Future()` binds
  the running loop as it is constructed. That was invisible while sockets were only ever
  built inside `asyncio.run`, and became load-bearing the moment a root client started
  owning sockets it may never use: constructing one in a synchronous test fixture raised
  `RuntimeError: There is no current event loop` before anything could connect.

  Deliberately a plain `def`, with no `pytest.mark.asyncio`, so no loop is running.
  """
  socket = RaisingSocket(url='wss://example.invalid')
  assert socket._ctx_future is None
