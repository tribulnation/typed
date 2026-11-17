"""Gateway WebSocket (v1): the REST queries and executes as JSON frames, one in flight at a
time.

v1 answers strictly in send order and its replies carry no correlation id (WebSocket v2
dispatches concurrently and replies out of order, correlated by an `id` only some executes
echo), so this socket sends one request, waits for the very next frame, and only then lets
the next request go. A request whose reply never arrives (timeout, cancellation, dropped
connection) closes the connection: its late reply would otherwise answer the next request.
"""

from typing_extensions import Any
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json

from typed_core.ws import SerialReplies, Socket

from ..exc import NetworkError

GATEWAY_MAX_SIZE = 2**24
"""Largest frame accepted, in bytes: `all_products` and `subaccount_info` dumps outgrow
`websockets`' 1 MiB default."""


@dataclass
class GatewaySocket(SerialReplies[str | bytes], Socket):
  """One gateway v1 connection, answering requests strictly in order.

  The server needs a ping frame at least every 30 s; `websockets`' own keepalive (a ping
  every 20 s, on by default) already sends it.
  """

  reply_timeout: timedelta = field(kw_only=True, default=timedelta(seconds=10))
  """Longest wait for one reply before the connection is given up."""

  def on_msg(self, msg: str | bytes):
    """Queue every frame as the reply to the request in flight: v1 pushes nothing else."""
    self.replies.put_nowait(msg)

  async def send(self, msg: object):
    """Write one JSON frame."""
    ws = await self.ws
    await ws.send(json.dumps(msg))

  async def call(self, msg: Any) -> str | bytes:
    """Send one request and return its raw reply frame.

    Raises:
      NetworkError: The connection dropped, or no reply came within `reply_timeout`; the
        connection is closed either way.
    """
    async with self.lock:
      ctx = await self.ctx
      try:
        await self.wait(self.send(msg), ctx=ctx)
        return await self.wait(
          asyncio.wait_for(self.replies.get(), self.reply_timeout.total_seconds()),
          ctx=ctx,
        )
      except BaseException as error:
        # The reply to this request may still arrive, and would then answer the next one.
        await self.close(ctx)
        if isinstance(error, asyncio.TimeoutError):
          raise NetworkError('Gateway WebSocket reply timed out') from error
        raise
