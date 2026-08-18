"""The root `Bit2Me` client: one field per surface (`spec/core.md`'s Surfaces
section), composed as peers. `.new()`/`.public()` are the only places credentials get
resolved — every surface just receives an already-resolved `Credentials | None`.
"""

from dataclasses import dataclass, field
from functools import cached_property
from typing_extensions import Self

from .core.auth import Credentials, resolve_credentials
from .core.transport.http import HttpRpcClient, BIT2ME_API_URL
from .core.transport.ws.trading import TradingWsClient, BIT2ME_TRADING_WS_URL
from .core.transport.ws.crypto import CryptoWsClient, BIT2ME_CRYPTO_WS_URL

from .api.v1 import V1
from .api.v2 import V2
from .streams.trading import TradingWs
from .streams.crypto import CryptoWs


@dataclass(kw_only=True)
class Bit2Me:
  http: HttpRpcClient
  """`http` surface — Crypto API, Embed API, Trading Spot REST."""
  trading_ws_client: TradingWsClient
  """`trading_ws` surface's transport, wrapped lazily below by `.trading_ws`."""
  crypto_ws_client: CryptoWsClient = field(default_factory=CryptoWsClient.new)
  """`crypto_ws` surface's transport, wrapped lazily below by `.crypto_ws`."""

  @cached_property
  def v1(self) -> V1:
    return V1(client=self.http)

  @cached_property
  def v2(self) -> V2:
    return V2(client=self.http)

  @cached_property
  def trading_ws(self) -> TradingWs:
    return TradingWs(client=self.trading_ws_client)

  @cached_property
  def crypto_ws(self) -> CryptoWs:
    return CryptoWs(client=self.crypto_ws_client)

  @classmethod
  def new(
    cls,
    api_key: str | None = None,
    api_secret: str | None = None,
    *,
    base_url: str = BIT2ME_API_URL,
    trading_ws_url: str = BIT2ME_TRADING_WS_URL,
    crypto_ws_url: str = BIT2ME_CRYPTO_WS_URL,
    public: bool = False,
    validate: bool = True,
  ) -> Self:
    """Build an authenticated client.

    Args:
      api_key: Bit2Me API key; read from `BIT2ME_API_KEY` when omitted.
      api_secret: Bit2Me API secret; read from `BIT2ME_SECRET_KEY` when omitted.
      base_url: `http` surface base URL, overridable for tests.
      trading_ws_url: `trading_ws` surface URL, overridable for tests.
      crypto_ws_url: `crypto_ws` surface URL, overridable for tests.
      public: Build a public-only client with no credentials, same as `.public()`.
      validate: Validate responses by default.
    """
    credentials = resolve_credentials(api_key, api_secret, public=public)
    return cls(
      http=HttpRpcClient(base_url=base_url, credentials=credentials, validate=validate),
      trading_ws_client=TradingWsClient.new(
        credentials=credentials,
        url=trading_ws_url,
        base_url=base_url,
        validate=validate,
      ),
      crypto_ws_client=CryptoWsClient.new(url=crypto_ws_url),
    )

  @classmethod
  def public(
    cls,
    *,
    base_url: str = BIT2ME_API_URL,
    trading_ws_url: str = BIT2ME_TRADING_WS_URL,
    validate: bool = True,
  ) -> Self:
    """Build a client restricted to public endpoints, needing no credentials."""
    return cls.new(
      base_url=base_url, trading_ws_url=trading_ws_url, public=True, validate=validate
    )

  async def __aenter__(self) -> Self:
    """Open the `http` surface. `trading_ws`/`crypto_ws` connect lazily, each on its
    own `async with` — see their respective classes."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)
