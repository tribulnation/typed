"""Root ownership for Spot HTTP, Spot sockets, public Futures REST and Charts."""

from typing_extensions import Self
from dataclasses import dataclass, field
from typed_core.http import HttpClient
from contextlib import AsyncExitStack

from ..futures.core import FuturesHttpClient
from ..charts.core import ChartsHttpClient
from .auth import TokenCache, resolve_credentials
from .transport.http import SPOT_API_URL, HttpRpcClient
from .transport.ws import SPOT_WS_AUTH_URL, SPOT_WS_URL, KrakenSocketClient


@dataclass(kw_only=True, frozen=True)
class StreamsBase:
  """The two physical WebSocket v2 connections `Streams` composes: public market data,
  and private (token-authenticated) channels -- the latter also shared with the
  top-level `TradingWs` surface (see `KrakenBase.new`, which builds both and passes the
  private one to each)."""

  private_client: KrakenSocketClient
  market_client: KrakenSocketClient

  @classmethod
  def new(
    cls, client: KrakenSocketClient, *, market_client: KrakenSocketClient
  ) -> Self:
    """Build from the two already-connected sockets `KrakenBase.new` constructs.

    Args:
      client: The private (token-authenticated) socket -- forwarded as `private_client`.
      market_client: The public socket.
    """
    return cls(private_client=client, market_client=market_client)

  async def __aenter__(self) -> Self:
    await self.private_client.__aenter__()
    await self.market_client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.private_client.__aexit__(exc_type, exc_value, traceback)
    await self.market_client.__aexit__(exc_type, exc_value, traceback)


@dataclass(kw_only=True)
class KrakenBase:
  """Build and own the transports backing every Kraken namespace.

  Spot private streams and WebSocket trading share the authenticated socket.
  Public Futures and Charts have independent HTTP transports and no credentials.
  """

  spot_client: HttpRpcClient
  market_client: KrakenSocketClient
  private_client: KrakenSocketClient
  futures_client: FuturesHttpClient = field(default_factory=FuturesHttpClient)
  charts_client: ChartsHttpClient = field(default_factory=ChartsHttpClient)
  _stack: AsyncExitStack | None = field(default=None, init=False, repr=False)

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    private_key: str | None = None,
    public: bool = False,
    validate: bool = True,
    http: HttpClient | None = None,
  ) -> Self:
    """Build a Kraken client with Spot and public Futures market data.

    Args:
      api_key: Kraken API key; read from `KRAKEN_API_KEY` when omitted.
      private_key: Kraken private key; read from `KRAKEN_PRIVATE_KEY` when omitted.
      public: Build a credential-free client, usable only for public endpoints/channels.
      validate: Validate responses by default.
      http: HTTP transport override; closed when this client exits.
    """
    credentials = resolve_credentials(api_key, private_key, public=public)
    spot_client = HttpRpcClient(
      base_url=SPOT_API_URL,
      credentials=credentials,
      validate=validate,
      http=http if http is not None else HttpClient(),
    )
    market_client = KrakenSocketClient.new(SPOT_WS_URL, validate=validate)
    private_client = KrakenSocketClient.new(
      SPOT_WS_AUTH_URL,
      token_cache=TokenCache() if credentials is not None else None,
      fetch_token=spot_client.get_ws_token if credentials is not None else None,
      validate=validate,
    )
    return cls(
      spot_client=spot_client,
      market_client=market_client,
      private_client=private_client,
      futures_client=FuturesHttpClient(
        validate=validate, http=http if http is not None else HttpClient()
      ),
      charts_client=ChartsHttpClient(
        validate=validate, http=http if http is not None else HttpClient()
      ),
    )

  async def __aenter__(self) -> Self:
    """Acquire owned transports and roll back partial acquisition on failure."""
    stack = AsyncExitStack()
    async with stack:
      await stack.enter_async_context(self.spot_client)
      await stack.enter_async_context(self.market_client)
      await stack.enter_async_context(self.private_client)
      await stack.enter_async_context(self.futures_client)
      await stack.enter_async_context(self.charts_client)
      self._stack = stack.pop_all()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close acquired transports in reverse order, including after a request failure."""
    if self._stack is not None:
      stack, self._stack = self._stack, None
      return await stack.__aexit__(exc_type, exc_value, traceback)
