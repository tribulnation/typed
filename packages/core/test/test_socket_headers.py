"""
Pin `Socket.headers`: extra HTTP headers sent with the opening handshake.

Some venues authenticate a WebSocket only at connect time, from a cookie or an account
header, with no in-band login. These tests run against a real local `websockets` server
that records each handshake's headers.
"""
from dataclasses import dataclass
import pytest
from websockets.asyncio.server import ServerConnection, serve
from websockets.http11 import Request

from typed_core.ws import Socket

@dataclass
class QuietSocket(Socket):
  """`Socket` that ignores every message: these tests only look at the handshake."""

  def on_msg(self, msg: str | bytes):
    """Drop the message."""

async def handler(connection: ServerConnection):
  """Keep the connection open until the client goes away."""
  await connection.wait_closed()

async def run(socket: QuietSocket, seen: list[Request], reconnect: dict[str, str] | None = None):
  """Open `socket` against a recording server, optionally swap its headers and reconnect."""
  def record(connection: ServerConnection, request: Request):
    """Remember the handshake request and let it through."""
    seen.append(request)

  async with serve(handler, 'localhost', 0, process_request=record) as server:
    port = next(iter(server.sockets)).getsockname()[1]
    socket.url = f'ws://localhost:{port}'
    async with socket:
      await socket.open()
      if reconnect is not None:
        socket.headers = reconnect
        await socket.close(await socket.ctx)
        await socket.open()

@pytest.mark.asyncio
async def test_headers_reach_the_handshake():
  """Every configured header arrives on the server's handshake request."""
  seen: list[Request] = []
  socket = QuietSocket('ws://unused', headers={'Cookie': 'gravity=abc', 'X-Account-Id': '42'})
  await run(socket, seen)
  assert len(seen) == 1
  assert seen[0].headers['Cookie'] == 'gravity=abc'
  assert seen[0].headers['X-Account-Id'] == '42'

@pytest.mark.asyncio
async def test_no_headers_by_default():
  """Without `headers`, the handshake carries none of them."""
  seen: list[Request] = []
  await run(QuietSocket('ws://unused'), seen)
  assert len(seen) == 1
  assert 'Cookie' not in seen[0].headers

@pytest.mark.asyncio
async def test_replaced_headers_apply_to_the_next_connection():
  """Headers are read on every connect, so a replacement is used from the next one on."""
  seen: list[Request] = []
  socket = QuietSocket('ws://unused', headers={'Cookie': 'gravity=old'})
  await run(socket, seen, reconnect={'Cookie': 'gravity=new'})
  assert [request.headers['Cookie'] for request in seen] == ['gravity=old', 'gravity=new']
