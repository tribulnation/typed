"""The Bybit v5 client root."""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from typed_bybit.core.auth import resolve_credentials
from typed_bybit.core.mixin import HttpClient, Region, resolve_rest_base_url
from typed_bybit.core.ws import resolve_ws_urls
from .http import Http
from .ws import Ws


@dataclass(kw_only=True)
class Bybit:
  """Bybit v5 client.

  Reaches every HTTP endpoint under `http` (`client.http.market.kline(...)`) and every
  WebSocket connection under `ws` (`client.ws.spot.orderbook(...)`, `client.ws.private`,
  `client.ws.trade`) from one object. Nothing connects until it's actually used, and
  closing the client only tears down the connections that were actually opened.

  Examples:
    ```python
    from typed_bybit import Bybit

    async with Bybit.new(public=True) as client:
      candles = await client.http.market.kline(symbol='BTCUSDT', interval='60')
    ```
  """

  http: Http
  ws: Ws

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    api_secret: str | None = None,
    public: bool = False,
    region: Region = 'global',
    testnet: bool = False,
    base_url: str | None = None,
    validate: bool = True,
    http: HttpClient | None = None,
  ) -> Self:
    """Create a Bybit client.

    Defaults to authenticated: `api_key`/`api_secret` fall back to the `BYBIT_API_KEY` /
    `BYBIT_API_SECRET` environment variables when not passed, and it is an error to
    build one with neither set. Pass `public=True` for a credential-free client
    restricted to the v5 Market endpoints.

    `region` and `testnet` are independent, freely combinable: `region` picks the
    domain, `testnet` picks the `api`/`api-testnet` (REST) or `stream`/`stream-testnet`
    (WebSocket) subdomain on it. Most regions document no testnet host and no dedicated
    WebSocket domain at all — see `resolve_rest_base_url`/`resolve_ws_urls` for exactly
    which do — so not every combination is confirmed to resolve to something live.
    Regional hosts also do **not** all list the same products; `region='eu'` in
    particular carries no derivatives.

    Args:
      api_key: Bybit API key; read from `BYBIT_API_KEY` when omitted.
      api_secret: Bybit API secret; read from `BYBIT_API_SECRET` when omitted.
      public: Build a credential-free client instead of requiring one.
      region: Documented regional entity to target.
      testnet: Target that region's testnet host instead of mainnet.
      base_url: Fully-qualified REST base URL override, for mocks or private gateways.
        WebSocket URLs are still resolved from `region`/`testnet` — there is no
        matching override for them.
      validate: Validate responses by default.
      http: Shared HTTP client override.

    Raises:
      ValueError: `region` is not a documented Bybit region.
      AuthError: `public` is false and no credentials were passed or found in the
        environment.

    References:
      - [Bybit v5 base endpoints](https://bybit-exchange.github.io/docs/v5/guide)
    """
    credentials = resolve_credentials(api_key, api_secret, public=public)
    rest_url = base_url or resolve_rest_base_url(region, testnet=testnet)
    ws_urls = resolve_ws_urls(region, testnet=testnet)
    return cls(
      http=Http.new(
        credentials=credentials, base_url=rest_url, validate=validate, http=http
      ),
      ws=Ws.new(credentials=credentials, urls=ws_urls),
    )

  async def __aenter__(self):
    await asyncio.gather(self.http.__aenter__(), self.ws.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http.__aexit__(exc_type, exc_value, traceback),
      self.ws.__aexit__(exc_type, exc_value, traceback),
    )
