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
from typed_core.http import HttpClient

from dataclasses import dataclass
import asyncio

from .auth import Credentials, resolve_credentials
from .transport.http import HttpRpcClient
from .transport.ws.api import SocketRpcClient
from .transport.ws.private_stream import PrivateStreamSocketClient
from .transport.ws.streams import SocketStreamClient
from .urls import (
  COINM_FUTURES_PRIVATE_STREAM_URL,
  COINM_FUTURES_STREAM_URL,
  COINM_FUTURES_URL,
  COINM_FUTURES_WS_API_URL,
  OPTIONS_PRIVATE_STREAM_URL,
  OPTIONS_STREAM_URL,
  OPTIONS_URL,
  PORTFOLIO_MARGIN_PRIVATE_STREAM_URL,
  PORTFOLIO_MARGIN_URL,
  SPOT_URL,
  STREAM_URL,
  USDM_FUTURES_PRIVATE_STREAM_URL,
  USDM_FUTURES_PUBLIC_STREAM_URL,
  USDM_FUTURES_STREAM_URL,
  USDM_FUTURES_URL,
  USDM_FUTURES_WS_API_URL,
  WS_API_URL,
  Urls,
)


@dataclass(kw_only=True, frozen=True)
class SpotClients:
  """Spot's own real transport clients: REST, market-data streams, and the WS API."""

  http_client: HttpRpcClient
  streams_client: SocketStreamClient
  ws_client: SocketRpcClient

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.http_client.__aenter__(),
      self.streams_client.__aenter__(),
      self.ws_client.__aenter__(),
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
      self.http_client.__aenter__(),
      self.streams_client.__aenter__(),
      self.public_streams_client.__aenter__(),
      self.private_streams_client.__aenter__(),
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
      self.http_client.__aenter__(),
      self.streams_client.__aenter__(),
      self.private_streams_client.__aenter__(),
      self.ws_client.__aenter__(),
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
      self.http_client.__aenter__(),
      self.streams_client.__aenter__(),
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
      self.http_client.__aenter__(),
      self.private_streams_client.__aenter__(),
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
    http: HttpClient | None = None,
    urls: Urls | None = None,
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
      http: HTTP transport override; closed when this client exits.
      urls: Base URL overrides per product (REST, market/public streams, user-data
        stream, WS API). Each takes precedence over the default; omitted ones keep it.
    """
    credentials: Credentials | None = resolve_credentials(
      api_key, secret_key, public=public
    )
    urls = urls or {}
    spot = urls.get('spot', {})
    usdm = urls.get('usdm_futures', {})
    coinm = urls.get('coinm_futures', {})
    options = urls.get('options', {})
    pm = urls.get('portfolio_margin', {})
    return cls(
      spot_clients=SpotClients(
        http_client=HttpRpcClient(
          http=http if http is not None else HttpClient(),
          base_url=spot.get('http') or SPOT_URL,
          credentials=credentials,
          recv_window=recv_window,
          validate=validate,
        ),
        streams_client=SocketStreamClient.new(
          url=spot.get('streams') or STREAM_URL, validate=validate
        ),
        ws_client=SocketRpcClient.new(
          url=spot.get('ws') or WS_API_URL,
          credentials=credentials,
          recv_window=recv_window,
          validate=validate,
        ),
      ),
      usdm_futures_clients=UsdMFuturesClients(
        http_client=HttpRpcClient(
          http=http if http is not None else HttpClient(),
          base_url=usdm.get('http') or USDM_FUTURES_URL,
          credentials=credentials,
          recv_window=recv_window,
          validate=validate,
        ),
        streams_client=SocketStreamClient.new(
          url=usdm.get('streams') or USDM_FUTURES_STREAM_URL, validate=validate
        ),
        public_streams_client=SocketStreamClient.new(
          url=usdm.get('public_streams') or USDM_FUTURES_PUBLIC_STREAM_URL,
          validate=validate,
        ),
        private_streams_client=PrivateStreamSocketClient(
          base_url=usdm.get('private_streams') or USDM_FUTURES_PRIVATE_STREAM_URL,
          validate=validate,
        ),
        ws_client=SocketRpcClient.new(
          url=usdm.get('ws') or USDM_FUTURES_WS_API_URL,
          credentials=credentials,
          recv_window=recv_window,
          validate=validate,
        ),
      ),
      coinm_futures_clients=CoinMFuturesClients(
        http_client=HttpRpcClient(
          http=http if http is not None else HttpClient(),
          base_url=coinm.get('http') or COINM_FUTURES_URL,
          credentials=credentials,
          recv_window=recv_window,
          validate=validate,
        ),
        streams_client=SocketStreamClient.new(
          url=coinm.get('streams') or COINM_FUTURES_STREAM_URL, validate=validate
        ),
        private_streams_client=PrivateStreamSocketClient(
          base_url=coinm.get('private_streams') or COINM_FUTURES_PRIVATE_STREAM_URL,
          validate=validate,
        ),
        ws_client=SocketRpcClient.new(
          url=coinm.get('ws') or COINM_FUTURES_WS_API_URL,
          credentials=credentials,
          recv_window=recv_window,
          validate=validate,
        ),
      ),
      options_clients=OptionsClients(
        http_client=HttpRpcClient(
          http=http if http is not None else HttpClient(),
          base_url=options.get('http') or OPTIONS_URL,
          credentials=credentials,
          recv_window=recv_window,
          validate=validate,
        ),
        streams_client=SocketStreamClient.new(
          url=options.get('streams') or OPTIONS_STREAM_URL, validate=validate
        ),
        private_streams_client=PrivateStreamSocketClient(
          base_url=options.get('private_streams') or OPTIONS_PRIVATE_STREAM_URL,
          validate=validate,
        ),
      ),
      portfolio_margin_clients=PortfolioMarginClients(
        http_client=HttpRpcClient(
          http=http if http is not None else HttpClient(),
          base_url=pm.get('http') or PORTFOLIO_MARGIN_URL,
          credentials=credentials,
          recv_window=recv_window,
          validate=validate,
        ),
        private_streams_client=PrivateStreamSocketClient(
          base_url=pm.get('private_streams') or PORTFOLIO_MARGIN_PRIVATE_STREAM_URL,
          validate=validate,
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
