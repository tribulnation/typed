"""The `crypto_ws` surface: account notifications. No subscribe/unsubscribe protocol
— one `authenticate` frame, then every notification type the account is entitled to
arrives unprompted on the same firehose. See `spec/core.md`'s Surfaces/WebSocket
sections.

`BIT2ME_CRYPTO_WS_URL` isn't stated directly in Bit2Me's docs (they give only an
unresolved `wss://${host}:${port}/` template), but is confirmed via Bit2Me's own
official sample repo (`github.com/bit2me-dev/bit2me-api-node-tool`) and independently
by a live connection: authenticating with a JWT token stays open cleanly. Use the
token form of `authenticate` — the documented `apikey`-array alternative reproducibly
gets an abrupt close (code `1006`) instead, isolated by an A/B test that changed only
the auth payload on the same connection/host.
"""

import asyncio
from dataclasses import dataclass, field
from typing_extensions import Any, Self, TypeVar, cast
import orjson

from typed_core.util import Stream, StreamManager
from typed_core.validation import validator
from typed_core.ws import Socket

BIT2ME_CRYPTO_WS_URL = 'wss://ws.bit2me.com/'

T = TypeVar('T')


@dataclass
class CryptoWsConnection(Socket):
  """One connection. `on_msg` only queues frames — there's no reply/push split to
  route, unlike `trading_ws`, since nothing here is request/reply shaped."""

  url: str = BIT2ME_CRYPTO_WS_URL
  queue: 'asyncio.Queue[dict[str, Any]]' = field(
    default_factory=asyncio.Queue, init=False, repr=False
  )

  def on_msg(self, msg: str | bytes):
    self.queue.put_nowait(orjson.loads(msg))

  async def send(self, msg: dict[str, Any]):
    """Send one command frame. `crypto_ws` never replies to a command on the wire —
    see `CryptoWsClient.request`."""
    ws = await self.ws
    await ws.send(orjson.dumps(msg))


@dataclass(kw_only=True)
class CryptoWsClient:
  """Implements `core.endpoint.crypto_ws.CryptoWsSocketClient` (`request()` for the
  `authenticate` command, `subscribe()` for the notification firehose) over one
  `CryptoWsConnection`."""

  conn: CryptoWsConnection = field(default_factory=CryptoWsConnection)
  validate: bool = True

  @classmethod
  def new(cls, *, url: str = BIT2ME_CRYPTO_WS_URL, validate: bool = True) -> Self:
    return cls(conn=CryptoWsConnection(url=url), validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  # CryptoWsSocketClient (typed_bit2me.core.endpoint.crypto_ws)

  async def request(self, path: str, params: dict[str, Any] | None = None):
    """Send `path`'s command frame. `crypto_ws` sends no reply to any command it
    defines — `authenticate`'s success case is silent, so this never awaits one."""
    await self.conn.send(params if params is not None else {'type': path})

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Every notification queued by `CryptoWsConnection.on_msg`, as one firehose —
    `channel` is unread: `crypto_ws` has exactly one, nothing to route on."""

    async def connect() -> Stream[Any, Any, Any]:
      async def stream():
        while True:
          yield await self.conn.wait(self.conn.queue.get())

      async def unsubscribe():
        """No-op: `crypto_ws` has no unsubscribe frame of its own — see
        `spec/core.md`'s Surfaces section."""
        return None

      return Stream(reply=None, stream=stream(), unsubscribe=unsubscribe)

    manager = StreamManager(connect=connect)
    if validator is not None and self.should_validate(validate):
      return manager.map(validator.python)
    return cast(StreamManager[T, Any, Any], manager)
