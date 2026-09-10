"""Bit2Me client root composition base (design §5c): a hand-written class holding each
of the client's three genuinely different transports -- one `http` connection shared by
`v1`/`v2`/`v3`, one `trading_ws` connection (commands + subscriptions), one `crypto_ws`
connection (the `authenticate` command and the notification firehose) -- built once in
`.new()`, never a single shared transport every child forwards unchanged. `Bit2Me`
(`main.py`, generated) composes `v1`/`v2`/`v3`/`trading_ws`/`crypto_ws` from the spec tree
via `codegen/config.toml`'s `children` mapping, through ordinary Python inheritance -- no
hand-written surface left on this base.
"""

from dataclasses import dataclass
from typing_extensions import Self

from .auth import Credentials, resolve_credentials
from .transport.http import BIT2ME_API_URL, HttpRpcClient
from .transport.ws.trading import BIT2ME_TRADING_WS_URL, TradingWsClient
from .transport.ws.crypto import BIT2ME_CRYPTO_WS_URL, CryptoWsClient


@dataclass(kw_only=True)
class Bit2MeBase:
  """Bit2Me client root: builds and owns the three physical transports every generated
  composite forwards unchanged."""

  http_client: HttpRpcClient
  trading_ws_client: TradingWsClient
  crypto_ws_client: CryptoWsClient

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
      public: Build a public-only client with no credentials.
      validate: Validate responses by default.
    """
    credentials = resolve_credentials(api_key, api_secret, public=public)
    return cls(
      http_client=HttpRpcClient(base_url=base_url, credentials=credentials, validate=validate),
      trading_ws_client=TradingWsClient.new(
        credentials=credentials,
        url=trading_ws_url,
        base_url=base_url,
        validate=validate,
      ),
      crypto_ws_client=CryptoWsClient.new(url=crypto_ws_url, validate=validate),
    )

  async def __aenter__(self) -> Self:
    """Open the `http` surface. `trading_ws`/`crypto_ws` connect lazily, each on its
    own `async with` — see their respective classes."""
    await self.http_client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http_client.__aexit__(exc_type, exc_value, traceback)
