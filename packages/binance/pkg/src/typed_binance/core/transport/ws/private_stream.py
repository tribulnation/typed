"""Private (listenKey-based) user-data stream transport.

USD-M Futures, Options, and Portfolio Margin each serve one always-on connection per
listenKey that pushes every private event for the account with no subscribe frame at all:
connecting the socket with a live listenKey already embedded in the URL path *is* the
subscription (see `spec/core.md`'s WebSocket section). `typed_core.ws.Socket` is exactly
this shape -- connect, get an `on_msg` callback per incoming frame, zero subscribe/channel
concept -- so this builds directly on it rather than `Streams`/`StreamsRpc`, both of which
assume a caller-issued subscribe frame this wire simply doesn't have.
"""

from typing_extensions import Any, Callable, Self
from dataclasses import dataclass, field
import asyncio
import json

from typed_core.util import Stream, StreamManager
from typed_core.validation import validator
from typed_core.ws import Socket


@dataclass
class PrivateStreamSocket(Socket):
  """One raw connect-only push connection for a single listenKey.

  Parses each incoming JSON frame and hands the decoded object to `on_event`. No `ping()`
  override -- Binance's private-stream hosts, like every other Binance WS host, ping the
  client periodically and `websockets` answers automatically; Binance never requires a
  client-sent ping first.
  """

  on_event: Callable[[dict], None] = field(default=lambda event: None)

  def on_msg(self, msg: str | bytes):
    self.on_event(json.loads(msg))


@dataclass(kw_only=True)
class PrivateStreamSocketClient:
  """Owns one product's private-stream host (`base_url`, no `<listenKey>` suffix).

  Structurally satisfies `typed_binance.core.endpoint.private_stream.PrivateStreamClient`.

  Each `connect()` call opens its own fresh `PrivateStreamSocket` for that one listenKey --
  unlike `SocketStreamClient`'s single shared combined-stream connection, a listenKey names
  an independent connection with its own lifecycle (start/keepalive/close via the product's
  own REST `listen_key_*` methods), so there is nothing to share across calls.
  """

  base_url: str
  validate: bool = True

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    """No shared connection to open -- each `connect()` call owns its own socket."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """No shared connection to close -- each open `connect()` stream closes itself via
    its own `StreamManager.unsubscribe`/`async with`.
    """

  def connect(
    self,
    listen_key: str,
    *,
    validator: 'validator[Any] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[Any, None, None]:
    """Build a `StreamManager` around one private user-data connection for `listen_key`."""
    _validator = validator if self.should_validate(validate) else None

    async def open() -> Stream[Any, None, None]:
      queue: 'asyncio.Queue[dict]' = asyncio.Queue()
      socket = PrivateStreamSocket(
        url=f'{self.base_url}/{listen_key}', on_event=queue.put_nowait
      )
      await socket.open()

      async def events():
        while True:
          event = await socket.wait(queue.get())
          yield _validator(event) if _validator is not None else event

      async def unsubscribe():
        await socket.__aexit__(None, None, None)
        return None

      return Stream(reply=None, stream=events(), unsubscribe=unsubscribe)

    return StreamManager(connect=open)
