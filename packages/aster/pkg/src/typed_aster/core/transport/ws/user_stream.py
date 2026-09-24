"""WebSocket transport for user-data streams: one connect-only connection per listenKey,
at `wss://<f|s|p>stream.../ws/<listenKey>`."""

from typing_extensions import Any, Callable, Self
from dataclasses import dataclass, field
import asyncio
import json

from typed_core.util import Stream, StreamManager
from typed_core.validation import validator
from typed_core.ws import Socket

from ...endpoint.user_stream import UserStreamClient
from ...exc import NetworkError, without_listen_key


@dataclass
class UserStreamSocket(Socket):
  """One raw user-data connection, handing each decoded event to `on_event`."""

  on_event: Callable[[Any], None] = field(default=lambda event: None)

  def on_msg(self, msg: str | bytes):
    self.on_event(json.loads(msg))


@dataclass(kw_only=True)
class UserStreamSocketClient(UserStreamClient):
  """User-data stream client for one surface's stream host (`base_url`, e.g.
  `wss://fstream.asterdex.com/ws`). Each `connect()` opens its own socket, closed when
  the returned stream is unsubscribed."""

  base_url: str
  validate: bool = True

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Nothing shared to close: each stream closes its own socket."""

  def connect(
    self,
    listen_key: str,
    *,
    validator: 'validator[Any] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[Any, None, None]:
    """Build a `StreamManager` around the user-data connection for `listen_key`."""
    event_validator = validator if self.should_validate(validate) else None

    async def open() -> Stream[Any, None, None]:
      queue: asyncio.Queue[Any] = asyncio.Queue()
      socket = UserStreamSocket(
        url=f'{self.base_url}/{listen_key}', on_event=queue.put_nowait
      )
      try:
        await socket.open()
      except NetworkError as e:
        raise without_listen_key(e, listen_key) from e.__cause__

      async def events():
        while True:
          event = await socket.wait(queue.get())
          yield event_validator(event) if event_validator is not None else event

      async def unsubscribe():
        await socket.__aexit__(None, None, None)

      return Stream(reply=None, stream=events(), unsubscribe=unsubscribe)

    return StreamManager(connect=open)
