"""Client root and per-product transport-client containers (design §5c). `BinanceBase`
holds one small container dataclass per product (`SpotClients`, ...) rather than the
transports directly, since each product composes a different, heterogeneous set of real
transports (spot: REST/streams/WS API; usdm_futures: REST/streams/public streams/private
stream/WS API; ...) -- design §5c's "aggregate one level further down inside Spot itself".
Construction still can't be generated: it needs real deployment URLs and resolved
credentials, neither a spec-level fact -- so this stays the one hand-written module that
builds every transport client and resolves shared credentials once, for every product to
share.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .auth import Credentials, resolve_credentials
from .transport.http import HttpRpcClient
from .transport.ws.api import SocketRpcClient
from .transport.ws.private_stream import PrivateStreamSocketClient
from .transport.ws.streams import SocketStreamClient

SPOT_URL = 'https://api.binance.com'
USDM_FUTURES_URL = 'https://fapi.binance.com'
COINM_FUTURES_URL = 'https://dapi.binance.com'
OPTIONS_URL = 'https://eapi.binance.com'
PORTFOLIO_MARGIN_URL = 'https://papi.binance.com'
STREAM_URL = 'wss://stream.binance.com:9443/stream'
USDM_FUTURES_STREAM_URL = 'wss://fstream.binance.com/market/stream'
USDM_FUTURES_PUBLIC_STREAM_URL = 'wss://fstream.binance.com/public/stream'
COINM_FUTURES_STREAM_URL = 'wss://dstream.binance.com/stream'
OPTIONS_STREAM_URL = 'wss://nbstream.binance.com/eoptions/stream'
WS_API_URL = 'wss://ws-api.binance.com:443/ws-api/v3'
USDM_FUTURES_WS_API_URL = 'wss://ws-fapi.binance.com/ws-fapi/v1'
COINM_FUTURES_WS_API_URL = 'wss://ws-dapi.binance.com/ws-dapi/v1'
USDM_FUTURES_PRIVATE_STREAM_URL = 'wss://fstream.binance.com/private/ws'
COINM_FUTURES_PRIVATE_STREAM_URL = 'wss://dstream.binance.com/ws'
OPTIONS_PRIVATE_STREAM_URL = 'wss://fstream.binance.com/private/ws'
PORTFOLIO_MARGIN_PRIVATE_STREAM_URL = 'wss://fstream.binance.com/pm/ws'


@dataclass(kw_only=True, frozen=True)
class SpotClients:
  """Spot's own real transport clients: REST, market-data streams, and the WS API."""

  http_client: HttpRpcClient
  streams_client: SocketStreamClient
  ws_client: SocketRpcClient

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.http_client.__aenter__(), self.streams_client.__aenter__(), self.ws_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http_client.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
      self.ws_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class UsdMFuturesClients:
  """USDⓈ-M Futures' own real transport clients: REST, market streams, public streams,
  the private user-data stream, and the WS API."""

  http_client: HttpRpcClient
  streams_client: SocketStreamClient
  public_streams_client: SocketStreamClient
  private_streams_client: PrivateStreamSocketClient
  ws_client: SocketRpcClient

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.http_client.__aenter__(), self.streams_client.__aenter__(),
      self.public_streams_client.__aenter__(), self.private_streams_client.__aenter__(),
      self.ws_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http_client.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
      self.public_streams_client.__aexit__(exc_type, exc_value, traceback),
      self.private_streams_client.__aexit__(exc_type, exc_value, traceback),
      self.ws_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class CoinMFuturesClients:
  """COIN-M Futures' own real transport clients: REST, market streams, the private
  user-data stream, and the WS API."""

  http_client: HttpRpcClient
  streams_client: SocketStreamClient
  private_streams_client: PrivateStreamSocketClient
  ws_client: SocketRpcClient

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.http_client.__aenter__(), self.streams_client.__aenter__(),
      self.private_streams_client.__aenter__(), self.ws_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http_client.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
      self.private_streams_client.__aexit__(exc_type, exc_value, traceback),
      self.ws_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class OptionsClients:
  """Options' own real transport clients: REST, market streams, and the private user-data
  stream."""

  http_client: HttpRpcClient
  streams_client: SocketStreamClient
  private_streams_client: PrivateStreamSocketClient

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.http_client.__aenter__(), self.streams_client.__aenter__(),
      self.private_streams_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http_client.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
      self.private_streams_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class PortfolioMarginClients:
  """Portfolio Margin's own real transport clients: REST and the private user-data
  stream."""

  http_client: HttpRpcClient
  private_streams_client: PrivateStreamSocketClient

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.http_client.__aenter__(), self.private_streams_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http_client.__aexit__(exc_type, exc_value, traceback),
      self.private_streams_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True)
class BinanceBase:
  """Binance client root: resolves one shared set of credentials, then builds every
  product's own real transport clients (`SpotClients`, ...) -- the fields design §5c's
  `[python.cores.root].children` forwards down into each generated product composite.
  """

  spot_clients: SpotClients
  usdm_futures_clients: UsdMFuturesClients
  coinm_futures_clients: CoinMFuturesClients
  options_clients: OptionsClients
  portfolio_margin_clients: PortfolioMarginClients

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    secret_key: str | None = None,
    public: bool = False,
    recv_window: int | None = None,
    validate: bool = True,
  ) -> Self:
    """Build a Binance client. Every surface shares one set of credentials -- Binance's
    HMAC signing scheme is uniform across REST hosts and, per docs (confirmed live), the
    WS API.

    Args:
      api_key: Binance API key; read from `BINANCE_API_KEY` when omitted.
      secret_key: HMAC secret; read from `BINANCE_SECRET_KEY` when omitted.
      public: Build a credential-free client -- only `NONE`-security endpoints work.
      recv_window: `recvWindow` (ms) sent with every signed request; `None` uses
        Binance's own 5000ms default.
      validate: Validate responses.
    """
    credentials: Credentials | None = resolve_credentials(api_key, secret_key, public=public)
    return cls(
      spot_clients=SpotClients(
        http_client=HttpRpcClient(
          base_url=SPOT_URL, credentials=credentials, recv_window=recv_window, validate=validate,
        ),
        streams_client=SocketStreamClient.new(url=STREAM_URL, validate=validate),
        ws_client=SocketRpcClient.new(
          url=WS_API_URL, credentials=credentials, recv_window=recv_window, validate=validate,
        ),
      ),
      usdm_futures_clients=UsdMFuturesClients(
        http_client=HttpRpcClient(
          base_url=USDM_FUTURES_URL, credentials=credentials, recv_window=recv_window, validate=validate,
        ),
        streams_client=SocketStreamClient.new(url=USDM_FUTURES_STREAM_URL, validate=validate),
        public_streams_client=SocketStreamClient.new(
          url=USDM_FUTURES_PUBLIC_STREAM_URL, validate=validate,
        ),
        private_streams_client=PrivateStreamSocketClient(
          base_url=USDM_FUTURES_PRIVATE_STREAM_URL, validate=validate,
        ),
        ws_client=SocketRpcClient.new(
          url=USDM_FUTURES_WS_API_URL, credentials=credentials, recv_window=recv_window,
          validate=validate,
        ),
      ),
      coinm_futures_clients=CoinMFuturesClients(
        http_client=HttpRpcClient(
          base_url=COINM_FUTURES_URL, credentials=credentials, recv_window=recv_window, validate=validate,
        ),
        streams_client=SocketStreamClient.new(url=COINM_FUTURES_STREAM_URL, validate=validate),
        private_streams_client=PrivateStreamSocketClient(
          base_url=COINM_FUTURES_PRIVATE_STREAM_URL, validate=validate,
        ),
        ws_client=SocketRpcClient.new(
          url=COINM_FUTURES_WS_API_URL, credentials=credentials, recv_window=recv_window,
          validate=validate,
        ),
      ),
      options_clients=OptionsClients(
        http_client=HttpRpcClient(
          base_url=OPTIONS_URL, credentials=credentials, recv_window=recv_window, validate=validate,
        ),
        streams_client=SocketStreamClient.new(url=OPTIONS_STREAM_URL, validate=validate),
        private_streams_client=PrivateStreamSocketClient(
          base_url=OPTIONS_PRIVATE_STREAM_URL, validate=validate,
        ),
      ),
      portfolio_margin_clients=PortfolioMarginClients(
        http_client=HttpRpcClient(
          base_url=PORTFOLIO_MARGIN_URL, credentials=credentials, recv_window=recv_window,
          validate=validate,
        ),
        private_streams_client=PrivateStreamSocketClient(
          base_url=PORTFOLIO_MARGIN_PRIVATE_STREAM_URL, validate=validate,
        ),
      ),
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.spot_clients.__aenter__(),
      self.usdm_futures_clients.__aenter__(),
      self.coinm_futures_clients.__aenter__(),
      self.options_clients.__aenter__(),
      self.portfolio_margin_clients.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.spot_clients.__aexit__(exc_type, exc_value, traceback),
      self.usdm_futures_clients.__aexit__(exc_type, exc_value, traceback),
      self.coinm_futures_clients.__aexit__(exc_type, exc_value, traceback),
      self.options_clients.__aexit__(exc_type, exc_value, traceback),
      self.portfolio_margin_clients.__aexit__(exc_type, exc_value, traceback),
    )
