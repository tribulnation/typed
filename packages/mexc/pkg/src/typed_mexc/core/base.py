"""MEXC client root: resolves one shared set of credentials, then builds every
product's own real transport clients (`SpotClients`/`FuturesClients`, design §5c) --
the fields `[python.cores.root].children` forwards down into each generated product
composite. MEXC's real shape needs one further level than a flat product split: each
product's own further HTTP/WebSocket-market/WebSocket-user split (design §5c's "one
level further down inside Spot itself" worked example, mexc's own real shape) --
`SpotClients`/`FuturesClients` (each defined beside its own product) bundle that
product's own already-built transports the same way `SpotClients`/`FuturesClients`'
own further `streams_client` bundles do one level deeper.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .auth import resolve_credentials
from .types import timestamp_millis
from typed_mexc.spot.core import MEXC_SPOT_API_BASE, SpotHttpClient, SpotClients
from typed_mexc.spot.streams.core import (
  MEXC_SPOT_SOCKET_URL, SpotPublicStreamsClient, SpotPrivateStreamsClient, SpotStreamsClients,
)
from typed_mexc.futures.core import MEXC_FUTURES_API_BASE, FuturesHttpClient, FuturesClients
from typed_mexc.futures.streams.core import (
  MEXC_FUTURES_SOCKET_URL, FuturesPublicStreamsClient, FuturesPrivateStreamsClient,
  FuturesStreamsClients,
)


@dataclass(kw_only=True)
class MexcBase:
  """MEXC client root: builds and owns every real transport every generated
  composite (`Spot`, `Futures`, and everything beneath them) forwards unchanged --
  one shared credential pair, resolved once, feeding both products' independent REST
  and WebSocket connections.
  """

  spot_clients: SpotClients
  futures_clients: FuturesClients

  @classmethod
  def new(
    cls,
    api_key: str | None = None,
    api_secret: str | None = None,
    *,
    public: bool = False,
    validate: bool = True,
    spot_base_url: str = MEXC_SPOT_API_BASE,
    spot_ws_url: str = MEXC_SPOT_SOCKET_URL,
    futures_base_url: str = MEXC_FUTURES_API_BASE,
    futures_ws_url: str = MEXC_FUTURES_SOCKET_URL,
  ) -> Self:
    """Create a MEXC client.

    Args:
      api_key: MEXC access key; read from `MEXC_ACCESS_KEY` when omitted.
      api_secret: MEXC secret key; read from `MEXC_SECRET_KEY` when omitted.
      public: Build a public-only client with no credentials.
      validate: Validate responses by default.
      spot_base_url: Spot REST base URL, overridable for tests.
      spot_ws_url: Spot WebSocket URL, overridable for tests.
      futures_base_url: Futures REST base URL, overridable for tests.
      futures_ws_url: Futures WebSocket URL, overridable for tests.
    """
    credentials = resolve_credentials(api_key, api_secret, public=public)
    spot_http = SpotHttpClient(base_url=spot_base_url, credentials=credentials, validate=validate)
    futures_http = FuturesHttpClient(
      base_url=futures_base_url, credentials=credentials, validate=validate,
    )
    return cls(
      spot_clients=SpotClients(
        http_client=spot_http,
        streams_client=SpotStreamsClients(
          market_client=SpotPublicStreamsClient(url=spot_ws_url),
          user_client=SpotPrivateStreamsClient(http=spot_http, url=spot_ws_url),
        ),
      ),
      futures_clients=FuturesClients(
        http_client=futures_http,
        streams_client=FuturesStreamsClients(
          market_client=FuturesPublicStreamsClient(url=futures_ws_url),
          user_client=FuturesPrivateStreamsClient(credentials=credentials, url=futures_ws_url),
        ),
      ),
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.spot_clients.__aenter__(), self.futures_clients.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.spot_clients.__aexit__(exc_type, exc_value, traceback),
      self.futures_clients.__aexit__(exc_type, exc_value, traceback),
    )
