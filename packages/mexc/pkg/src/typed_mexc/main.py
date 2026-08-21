"""The MEXC client root, composing the independent spot and futures surfaces."""

from dataclasses import dataclass
import asyncio

from .core.auth import resolve_credentials
from .spot import Spot
from .spot.core import MEXC_SPOT_API_BASE
from .spot.streams.core import MEXC_SPOT_SOCKET_URL
from .futures import Futures
from .futures.core import MEXC_FUTURES_API_BASE
from .futures.streams.core import MEXC_FUTURES_SOCKET_URL


@dataclass
class MEXC:
  """MEXC client, composing the independently-transported spot and futures surfaces.

  Examples:
    ```python
    from typed_mexc import MEXC

    async with MEXC.new(public=True) as client:
      result = await client.spot.market.ping()
    ```
  """

  spot: Spot
  futures: Futures

  @classmethod
  def new(
    cls, api_key: str | None = None, api_secret: str | None = None, *,
    public: bool = False,
    validate: bool = True,
    spot_base_url: str = MEXC_SPOT_API_BASE,
    spot_ws_url: str = MEXC_SPOT_SOCKET_URL,
    futures_base_url: str = MEXC_FUTURES_API_BASE,
    futures_ws_url: str = MEXC_FUTURES_SOCKET_URL,
  ):
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
    creds = resolve_credentials(api_key, api_secret, public=public)
    return cls(
      spot=Spot.new(
        api_key=creds.api_key if creds else None,
        api_secret=creds.api_secret if creds else None,
        public=public,
        base_url=spot_base_url,
        ws_url=spot_ws_url,
        default_validate=validate,
      ),
      futures=Futures.new(
        api_key=creds.api_key if creds else None,
        api_secret=creds.api_secret if creds else None,
        public=public,
        base_url=futures_base_url,
        ws_url=futures_ws_url,
        default_validate=validate,
      ),
    )

  async def __aenter__(self):
    """Open the underlying spot and futures transports."""
    await asyncio.gather(
      self.spot.__aenter__(),
      self.futures.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the underlying spot and futures transports."""
    await asyncio.gather(
      self.spot.__aexit__(exc_type, exc_value, traceback),
      self.futures.__aexit__(exc_type, exc_value, traceback),
    )
