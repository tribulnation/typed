"""
Pin `Socket.max_size`: the largest incoming message a socket accepts.

Some venues push single frames over `websockets`' 1 MiB default (a full protocol-state
snapshot, say). These tests run against a real local `websockets` server that sends one
2 MiB message as soon as a client connects.
"""
from dataclasses import dataclass, field
import asyncio

import pytest
from websockets.asyncio.server import ServerConnection, serve

from typed_core.ws import Socket

BIG = 'x' * (2 * 2**20)
"""A message twice `websockets`' default limit."""
TIMEOUT = 5

@dataclass
class RecordingSocket(Socket):
  """`Socket` that keeps every message it receives."""
  received: list[str | bytes] = field(default_factory=list, init=False)

  def on_msg(self, msg: str | bytes):
    """Remember the message."""
    self.received.append(msg)

async def handler(connection: ServerConnection):
  """Send one oversized message, then stay open until the client goes away."""
  await connection.send(BIG)
  await connection.wait_closed()

async def run(socket: RecordingSocket) -> int | None:
  """
  Open `socket` against the server and wait for the message or a close.

  Returns:
    The close code the client sent, or `None` while the connection is still open.
  """
  async with serve(handler, 'localhost', 0, max_size=None) as server:
    port = next(iter(server.sockets)).getsockname()[1]
    socket.url = f'ws://localhost:{port}'
    async with socket:
      ctx = await socket.open()
      async def settled():
        """Wait until the message arrived or the connection closed."""
        while not socket.received and ctx.ws.close_code is None:
          await asyncio.sleep(0.01)
      await asyncio.wait_for(settled(), TIMEOUT)
      sent = ctx.ws.protocol.close_sent
      return None if sent is None else sent.code

@pytest.mark.asyncio
async def test_default_limit_closes_on_a_larger_message():
  """Over the 1 MiB default, the connection closes with 1009 and nothing is delivered."""
  socket = RecordingSocket('ws://unused')
  assert await run(socket) == 1009
  assert socket.received == []

@pytest.mark.asyncio
async def test_raised_limit_delivers_a_larger_message():
  """A raised `max_size` delivers the message whole."""
  socket = RecordingSocket('ws://unused', max_size=4 * 2**20)
  assert await run(socket) is None
  assert socket.received == [BIG]

@pytest.mark.asyncio
async def test_no_limit_delivers_a_larger_message():
  """`max_size=None` lifts the limit."""
  socket = RecordingSocket('ws://unused', max_size=None)
  assert await run(socket) is None
  assert socket.received == [BIG]
