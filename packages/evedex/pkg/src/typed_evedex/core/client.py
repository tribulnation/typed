"""The root's hand-written base: credentials, transports and lifecycle."""

from typing_extensions import Self
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio

from typed_core.http import HttpClient

from .auth import Credentials, Session, resolve_credentials
from .environments import ENVIRONMENTS, Environment, EnvironmentProfile
from .transport.http import HttpRpcClient
from .transport.ws import SocketStreamClient


@dataclass(kw_only=True)
class ClientBase:
  """Builds and owns one transport per surface: the three REST services share one
  connection pool and one wallet session; the WebSocket connects lazily.

  The generated root (`Evedex`) composes each surface over the matching field.
  """

  exchange_client: HttpRpcClient = field(repr=False)
  """Exchange (`trading-api`) REST transport; takes the API key."""
  auth_client: HttpRpcClient = field(repr=False)
  """Auth (`auth-api`) REST transport; session only."""
  market_data_client: HttpRpcClient = field(repr=False)
  """Market-data (`market-data-api`) REST transport; session only."""
  streams_client: SocketStreamClient = field(repr=False)
  """Centrifugo WebSocket transport."""
  credentials: Credentials | None = field(default=None, repr=False)
  http: HttpClient = field(default_factory=HttpClient, repr=False)
  """The connection pool every REST surface shares, owned by this root."""

  @classmethod
  def new(
    cls,
    *,
    env: Environment | EnvironmentProfile = 'prod',
    private_key: str | None = None,
    api_key: str | None = None,
    address: str | None = None,
    public: bool = False,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    http: HttpClient | None = None,
  ) -> Self:
    """Build a client.

    Credentials default to environment variables under the environment's prefix
    (`EVEDEX_` on prod, `EVEDEX_DEMO_` on demo): `PRIVATE_KEY`, `API_KEY`, `ADDRESS`.

    Args:
      env: `prod` (evedex.com), `demo` (evedex.io), or a custom profile.
      private_key: Wallet private key: signs in, signs orders, opens private channels.
      api_key: API key: private Exchange REST reads without a wallet. Preferred over the
        wallet's session on the services that accept it.
      address: Expected wallet address, checked against the key's.
      public: Build without credentials, for public data only.
      validate: Validate responses.
      timeout: HTTP request and WebSocket connect timeout. A passed `http` keeps its
        own request timeout.
      http: Shared HTTP client override, reused by every REST service and the wallet
        session; closed when this client exits.

    Raises:
      AuthError: `public` is false and no credential was passed or found.

    Examples:
      ```python
      from typed_evedex import Evedex

      async with Evedex.new(public=True) as client:
        info = await client.exchange.market.info()
      ```
    """
    profile = ENVIRONMENTS[env] if isinstance(env, str) else env
    credentials = resolve_credentials(
      profile, private_key=private_key, api_key=api_key, address=address, public=public
    )
    if http is None:
      http = HttpClient(timeout=timeout.total_seconds())
    session = None
    if credentials is not None and credentials.account is not None:
      session = Session(account=credentials.account, profile=profile, http=http)

    def rest(base_url: str, *, accepts_api_key: bool) -> HttpRpcClient:
      """One REST service client over the shared pool and session."""
      return HttpRpcClient(
        base_url=base_url,
        http=http,
        credentials=credentials,
        session=session,
        chain_id=profile.chain_id,
        accepts_api_key=accepts_api_key,
        validate=validate,
      )

    return cls(
      exchange_client=rest(profile.exchange_url, accepts_api_key=True),
      auth_client=rest(profile.auth_url, accepts_api_key=False),
      market_data_client=rest(profile.market_data_url, accepts_api_key=False),
      streams_client=SocketStreamClient.new(
        profile.ws_url,
        prefix=profile.channel_prefix,
        session=session,
        validate=validate,
        timeout=timeout,
      ),
      credentials=credentials,
      http=http,
    )

  async def __aenter__(self) -> Self:
    """Open the shared HTTP pool and take ownership of the WebSocket (opened lazily)."""
    await self.http.__aenter__()
    await self.streams_client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the HTTP pool and the WebSocket, if one was opened."""
    await asyncio.gather(
      self.http.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
    )
