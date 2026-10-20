"""WebSocket transport for the v1 streams: one connection per subscription, at
`<stream base>/<path>?<query>`, with no client frames at all.

The server pushes from the moment the connection opens and pings every 15 seconds
(answered automatically by the WebSocket library). The `User-Agent` header is mandatory
on the upgrade, and the account stream also needs `X-Api-Key`.
"""

from typing_extensions import Any, Callable, Mapping, Self
from dataclasses import dataclass, field
from urllib.parse import urlencode
import asyncio

from typed_core.util import Stream, StreamManager
from typed_core.validation import validator
from typed_core.ws import Socket
import websockets

from ..auth import Credentials
from ..endpoint.stream import StreamClient
from ..endpoint.wire import query_values
from ..envelope import decode
from ..exc import AuthError, NetworkError, RateLimited
from .http import DEFAULT_USER_AGENT


@dataclass
class StreamSocket(Socket):
  """One raw stream connection, handing each decoded message to `on_message`."""

  on_message: Callable[[Any], None] = field(default=lambda message: None)

  def on_msg(self, msg: str | bytes):
    """Decode a pushed frame (non-integer numbers as `Decimal`) and hand it over."""
    self.on_message(decode(msg if isinstance(msg, str) else msg.decode()))


def handshake_error(error: NetworkError) -> Exception:
  """The exception a failed connect stands for: `AuthError` for a `401`/`403` upgrade,
  `RateLimited` for `429`, the original `NetworkError` otherwise."""
  cause = error.__cause__
  if isinstance(cause, websockets.exceptions.InvalidStatus):
    status = cause.response.status_code
    if status in (401, 403):
      return AuthError(status, 'Stream upgrade rejected: missing or invalid API key')
    if status == 429:
      return RateLimited(status, 'Stream upgrade rate limited')
  return error


@dataclass(kw_only=True)
class SocketStreamClient(StreamClient):
  """Stream client for one deployment's v1 stream host. Each subscription opens its own
  socket, closed when the stream is unsubscribed (or when the root client exits)."""

  base_url: str
  """WebSocket v1 base URL."""
  credentials: Credentials | None = None
  """Holds the API key the account stream sends; `None` for public streams only."""
  user_agent: str = DEFAULT_USER_AGENT
  """`User-Agent` header, mandatory on the upgrade."""
  validate: bool = True
  """Validate pushed messages by default."""
  sockets: list[StreamSocket] = field(default_factory=list, init=False, repr=False)
  """Open connections, closed together when the root client exits."""

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    """Take ownership; nothing connects until a stream is subscribed."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close every stream still open."""
    sockets, self.sockets = self.sockets, []
    await asyncio.gather(
      *(socket.__aexit__(exc_type, exc_value, traceback) for socket in sockets),
      return_exceptions=True,
    )

  def headers(self, *, authed: bool) -> dict[str, str]:
    """Upgrade headers: `User-Agent` always, `X-Api-Key` when `authed`.

    Raises:
      AuthError: `authed`, and the client was built with `public=True`.
    """
    headers = {'User-Agent': self.user_agent}
    if authed:
      if self.credentials is None:
        raise AuthError(
          'This stream needs an API key: build the client with credentials, not `public=True`.'
        )
      headers['X-Api-Key'] = self.credentials.api_key
    return headers

  def url(self, path: str, params: Mapping[str, Any] | None) -> str:
    """The full stream URL for `path` and its query parameters."""
    query = urlencode(query_values(params), doseq=True) if params else ''
    return self.base_url + path + (f'?{query}' if query else '')

  def subscribe(
    self,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    authed: bool = False,
    validator: 'validator[Any] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[Any, None, None]:
    """Build a `StreamManager` around the connection for one stream. Nothing connects until
    it is awaited or entered; unsubscribing closes the connection.

    Args:
      path: Stream path below the v1 base, e.g. `/orderbooks/BTC-USD`.
      params: Query parameters, e.g. `{'depth': 1}`.
      authed: Send the API key on the upgrade.
      validator: Message validator.
      validate: Per-call override of message validation.
    """
    message_validator = validator if self.should_validate(validate) else None

    async def connect() -> Stream[Any, None, None]:
      """Open the connection and expose its messages as a stream."""
      queue: asyncio.Queue[Any] = asyncio.Queue()
      arrived = asyncio.Event()

      def on_message(message: Any):
        """Queue a pushed message and wake the reader."""
        queue.put_nowait(message)
        arrived.set()

      socket = StreamSocket(
        url=self.url(path, params),
        headers=self.headers(authed=authed),
        on_message=on_message,
      )
      try:
        ctx = await socket.open()
      except NetworkError as e:
        raise handshake_error(e) from e.__cause__
      self.sockets.append(socket)

      async def messages():
        """Each pushed message, validated, from this subscription's one connection.

        Every frame the connection delivered is yielded, then the stream raises the
        connection's failure (`NetworkError` on a close) instead of reconnecting: a
        silent reconnect would hide the gap in `seq` from the caller.
        """
        # Not `socket.wait(queue.get(), ctx=ctx)`: it fails as soon as `Context.alive`
        # sees the close, possibly before the listener has delivered the frames still
        # buffered, and drops a frame its `queue.get()` popped in the same tick. Ending
        # only once the listener (or pinger) is done and the queue is drained keeps them.
        while True:
          while queue.empty():
            if ctx.listener.done() or ctx.pinger.done():
              raise ctx.failure()
            arrived.clear()
            wake = asyncio.ensure_future(arrived.wait())
            try:
              await asyncio.wait(
                [wake, ctx.listener, ctx.pinger], return_when='FIRST_COMPLETED'
              )
            finally:
              wake.cancel()
          message = queue.get_nowait()
          yield (
            message_validator.python(message)
            if message_validator is not None
            else message
          )

      async def unsubscribe():
        """Close this stream's connection."""
        self.sockets = [
          open_socket for open_socket in self.sockets if open_socket is not socket
        ]
        await socket.__aexit__(None, None, None)

      return Stream(reply=None, stream=messages(), unsubscribe=unsubscribe)

    return StreamManager(connect=connect)
