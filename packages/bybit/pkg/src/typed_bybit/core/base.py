"""Bybit client root base (design §5c): a hand-written class holding every heterogeneous
child's already-built transport -- one shared REST transport plus nine independent
WebSocket connections -- wrapped by the generated `Bybit` composite (`main.py`).

`Bybit` composes ten genuinely different client kinds as siblings, not variations of one
shared transport: `client` (REST, shared by every `market`/`account`/`asset`/... product
domain) and nine WebSocket sockets, one per real connection (`spot`, `linear`, `inverse`,
`option`, `private`, `spread_ws`, `rfq_ws`, `finance_ws`, `trade_ws`) -- design §5c's
worked shape, applied at the root exactly as it is at any other position.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from typed_core.http import HttpClient

from .auth import Credentials, resolve_credentials
from .http import BYBIT_API_URL, HttpTransport, Region, resolve_rest_base_url
from .ws import BybitStreamsClient, BybitTradeClient, resolve_ws_urls


@dataclass(kw_only=True)
class BybitBase:
  """Bybit v5 client root: builds and owns the ten physical transports every generated
  product/connection subtree forwards unchanged -- one shared HTTP transport, and one
  dedicated WebSocket socket per real connection."""

  client: HttpTransport
  spot_client: BybitStreamsClient
  linear_client: BybitStreamsClient
  inverse_client: BybitStreamsClient
  option_client: BybitStreamsClient
  private_client: BybitStreamsClient
  spread_client: BybitStreamsClient
  rfq_client: BybitStreamsClient
  finance_client: BybitStreamsClient
  trade_client: BybitTradeClient

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

    Defaults to authenticated: `api_key`/`api_secret` fall back to `region`'s own
    environment variables when not passed (`BYBIT_API_KEY`/`BYBIT_API_SECRET` for
    `region='global'`, `BYBIT_EU_API_KEY`/`BYBIT_EU_API_SECRET` for `region='eu'`, and so
    on), and it is an error to build one with neither set — Bybit's regional entities are
    separate accounts with separate keys, so there is no cross-region fallback to guess
    through (`resolve_credentials`'s own docstring). Pass `public=True` for a
    credential-free client restricted to the v5 Market endpoints and public streams.

    `region` and `testnet` are independent, freely combinable: `region` picks the
    domain, `testnet` picks the `api`/`api-testnet` (REST) or `stream`/`stream-testnet`
    (WebSocket) subdomain on it. Most regions document no testnet host and no dedicated
    WebSocket domain at all — see `resolve_rest_base_url`/`resolve_ws_urls` for exactly
    which do — so not every combination is confirmed to resolve to something live.
    Regional hosts also do **not** all list the same products; `region='eu'` in
    particular carries no derivatives.

    Nothing connects until it's actually used, and closing the client (`async with`)
    only tears down the connections that were actually opened.

    Args:
      api_key: Bybit API key; read from the environment when omitted (see `region`).
      api_secret: Bybit API secret; read from the environment when omitted (see `region`).
      public: Build a credential-free client instead of requiring one.
      region: Documented regional entity to target; also selects which environment
        variables `api_key`/`api_secret` fall back to.
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
    credentials = resolve_credentials(api_key, api_secret, public=public, region=region)
    rest_url = base_url or resolve_rest_base_url(region, testnet=testnet)
    ws_urls = resolve_ws_urls(region, testnet=testnet)
    return cls(
      client=HttpTransport(
        base_url=rest_url, http=http or HttpClient(), validate=validate,
        credentials=credentials,
      ),
      spot_client=BybitStreamsClient(url=ws_urls['spot']),
      linear_client=BybitStreamsClient(url=ws_urls['linear']),
      inverse_client=BybitStreamsClient(url=ws_urls['inverse']),
      option_client=BybitStreamsClient(url=ws_urls['option']),
      spread_client=BybitStreamsClient(url=ws_urls['spread']),
      rfq_client=BybitStreamsClient(url=ws_urls['rfq']),
      private_client=BybitStreamsClient(
        url=ws_urls['private'], credentials=credentials, require_auth=True,
      ),
      finance_client=BybitStreamsClient(url=ws_urls['fp']),
      trade_client=BybitTradeClient(url=ws_urls['trade'], credentials=credentials),
    )

  def _sockets(self) -> tuple[BybitStreamsClient | BybitTradeClient, ...]:
    return (
      self.spot_client,
      self.linear_client,
      self.inverse_client,
      self.option_client,
      self.private_client,
      self.spread_client,
      self.rfq_client,
      self.finance_client,
      self.trade_client,
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.client.__aenter__(), *(s.__aenter__() for s in self._sockets()))
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.client.__aexit__(exc_type, exc_value, traceback),
      *(s.__aexit__(exc_type, exc_value, traceback) for s in self._sockets()),
    )
