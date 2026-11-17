"""The authenticated Kraken Futures client: signed REST and the WebSocket feeds."""

from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from functools import cached_property
from typing_extensions import Literal, Self

from typed_core.http import HttpClient

from .auth import resolve_futures_credentials
from .http import DEMO_FUTURES_URL, FUTURES_URL, SignedFuturesHttpClient
from .rest import FuturesTrading
from .ws import DEMO_FUTURES_WS_URL, FUTURES_WS_URL, FuturesSocket, FuturesStreams

FuturesEnvironment = Literal['live', 'demo']
"""`live` is futures.kraken.com, `demo` the separate demo-futures.kraken.com."""


@dataclass(kw_only=True)
class KrakenFutures:
  """Kraken Futures with a Futures API key: account, orders and private feeds.

  Futures keys are not Spot keys: create them in the Futures site's API settings.
  REST and the WebSocket connect lazily on first use.

  Examples:
    ```python
    from typed_kraken.futures_trading import KrakenFutures

    async with KrakenFutures.new() as client:
      accounts = await client.trading.accounts()
      async with client.streams.fills() as fills:
        async for message in fills:
          print(message)
    ```

  References:
    - [Futures API](https://docs.kraken.com/api/docs/futures-api/trading/account-information)
  """

  http: SignedFuturesHttpClient
  socket: FuturesSocket
  validate: bool = True
  _stack: AsyncExitStack | None = field(default=None, init=False, repr=False)

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    private_key: str | None = None,
    environment: FuturesEnvironment = 'live',
    public: bool = False,
    validate: bool = True,
    base_url: str | None = None,
    ws_url: str | None = None,
    http: HttpClient | None = None,
  ) -> Self:
    """Build a client, reading missing credentials from the environment.

    Args:
      api_key: Futures API key; read from `KRAKEN_FUTURES_API_KEY` when omitted.
      private_key: Futures API secret; read from `KRAKEN_FUTURES_PRIVATE_KEY` when omitted.
      environment: `live` or `demo`.
      public: Build without credentials: only public calls and feeds work.
      validate: Validate responses by default.
      base_url: REST base URL override.
      ws_url: WebSocket URL override.
      http: Shared HTTP transport; closed when this client exits.
    """
    credentials = resolve_futures_credentials(api_key, private_key, public=public)
    demo = environment == 'demo'
    signed = SignedFuturesHttpClient(
      base_url=base_url or (DEMO_FUTURES_URL if demo else FUTURES_URL),
      http=http if http is not None else HttpClient(),
      validate=validate,
      credentials=credentials,
    )
    socket = FuturesSocket(
      url=ws_url or (DEMO_FUTURES_WS_URL if demo else FUTURES_WS_URL),
      credentials=credentials,
    )
    return cls(http=signed, socket=socket, validate=validate)

  @property
  def authenticated(self) -> bool:
    """Whether the client holds credentials."""
    return self.http.credentials is not None

  @cached_property
  def trading(self) -> FuturesTrading:
    """Signed REST: accounts, positions, orders, fills, leverage and fees."""
    return FuturesTrading(client=self.http)

  @cached_property
  def streams(self) -> FuturesStreams:
    """WebSocket feeds: books, and own fills, orders, positions and balances."""
    return FuturesStreams(socket=self.socket, validate=self.validate)

  async def __aenter__(self) -> Self:
    """Own both transports; neither connects until used."""
    stack = AsyncExitStack()
    async with stack:
      await stack.enter_async_context(self.http)
      await stack.enter_async_context(self.socket)
      self._stack = stack.pop_all()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close whatever was opened, in reverse order."""
    if self._stack is not None:
      stack, self._stack = self._stack, None
      return await stack.__aexit__(exc_type, exc_value, traceback)
