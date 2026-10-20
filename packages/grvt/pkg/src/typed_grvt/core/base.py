"""Root lifecycle: builds and owns the three surface clients every GRVT endpoint calls into."""

from dataclasses import dataclass
from datetime import timedelta

from typing_extensions import Self

from typed_core.http import HttpClient

from .auth import ENV_PREFIXES, Session, resolve_credentials
from .env import Environment, Hosts
from .lookup import Lookup
from .owners import Owned
from .signing import Signer
from .transport.edge import EdgeTransport
from .transport.gateway import GatewayTransport
from .transport.ws import GatewaySocket


@dataclass(kw_only=True)
class ClientBase(Owned):
  """The three GRVT surfaces' clients, built once by `.new()`.

  - `market_client`: market-data gateway, public.
  - `trading_client`: trading gateway, authenticated by the session, signing with the
    private key.
  - `edge_client`: edge REST host, authenticated by the same session.

  Each owns its own `HttpClient`, so leaving one surface's `async with` never closes a
  connection pool another surface is still using. Every one of them counts its `async with`
  owners and closes its connections only when the last one leaves, so any surface's block
  (`client.market`, `client.market_streams`, `client.trading`, `client.trading_streams`,
  `client.edge`) nested inside `async with client`, or inside another surface's block, keeps
  them open for the outer block, and the outermost exit closes them. What is shared counts
  its owners the same way: the session's login connection (shared by `trading_client` and
  `edge_client`), and `market_client` (whose market data the trading gateway signs with). So
  `async with client.trading` alone closes everything it opened.

  The counting is synchronous (`Owned`): a task cancelled while entering or leaving any of
  these blocks leaves no owner behind, and the closes the outermost exit starts complete
  even if it is cancelled meanwhile.
  """

  market_client: GatewayTransport
  trading_client: GatewayTransport
  edge_client: EdgeTransport
  session: Session | None = None
  """The session shared by `trading_client` and `edge_client`; `None` on a public client."""

  @classmethod
  def new(
    cls,
    *,
    env: Environment = 'prod',
    api_key: str | None = None,
    private_key: str | None = None,
    trading_account_id: str | None = None,
    public: bool = False,
    validate: bool = True,
    signature_ttl: timedelta = timedelta(days=1),
    timeout: float = 10.0,
  ) -> Self:
    """Build a GRVT client.

    Connects to production unless `env` says otherwise. When neither `api_key` nor
    `private_key` is passed, credentials are read from `{prefix}API_KEY`,
    `{prefix}PRIVATE_KEY` and `{prefix}TRADING_ACCOUNT_ID`, where the prefix is `GRVT_` for
    `prod`, `GRVT_TESTNET_` for `testnet` and `GRVT_STAGING_` for `staging`, so a testnet
    credential is never sent to production. Passing either secret reads nothing from the
    environment, so an explicit key is never mixed with another account's.

    Args:
      env: GRVT environment: `prod`, or `testnet`/`staging` to opt into a test deployment.
      api_key: API key, exchanged for the session cookie.
      private_key: EIP-712 signer key (the API key's signer); needed for orders,
        transfers and withdrawals. Without an API key, it logs in as a funding wallet.
      trading_account_id: Default trading sub-account id, used by every trading call that
        leaves its `sub_account_id` out; defaults to `{prefix}TRADING_ACCOUNT_ID` when
        credentials come from the environment, else to the one the API key is scoped to.
      public: Build a market-data-only client, with no credentials.
      validate: Validate responses by default.
      signature_ttl: Lifetime of generated payload signatures (at most 30 days), and so
        also the default expiry of every `GOOD_TILL_TIME` order; pin a payload's
        `signature.expiration` to override it for one order.
      timeout: Request timeout, in seconds: of each HTTP request, and of each WebSocket
        handshake and JSON-RPC reply.

    Raises:
      AuthError: `public` is false and no API key or private key was found, or the
        private key is malformed (the message never includes it).
    """
    hosts = Hosts.of(env)
    credentials = resolve_credentials(
      env,
      api_key=api_key,
      private_key=private_key,
      trading_account_id=trading_account_id,
      public=public,
    )
    signer = session = None
    if credentials is not None:
      if credentials.private_key:
        signer = Signer.from_key(credentials.private_key, chain_id=hosts.chain_id)
      session = Session(
        edge_url=hosts.edge,
        api_key=credentials.api_key,
        signer=signer,
        http=HttpClient(timeout=timeout),
      )
    # Named in the "no default sub-account" error only when it was actually read.
    account_var = (
      f'{ENV_PREFIXES[env]}TRADING_ACCOUNT_ID'
      if credentials is not None and credentials.source == 'environment'
      else None
    )
    ws_timeout = timedelta(seconds=timeout)
    market = GatewayTransport(
      base_url=hosts.market_data,
      socket=GatewaySocket(hosts.market_data_ws, timeout=ws_timeout),
      http=HttpClient(timeout=timeout),
      validate=validate,
    )
    trading = GatewayTransport(
      base_url=hosts.trades,
      socket=GatewaySocket(hosts.trades_ws, session=session, timeout=ws_timeout),
      http=HttpClient(timeout=timeout),
      session=session,
      authenticated=True,
      signer=signer,
      lookup=Lookup(market=market),
      signature_ttl=signature_ttl,
      trading_account_id=credentials.trading_account_id if credentials else None,
      trading_account_var=account_var,
      validate=validate,
    )
    edge = EdgeTransport(
      base_url=hosts.edge,
      http=HttpClient(timeout=timeout),
      session=session,
      validate=validate,
    )
    return cls(
      market_client=market,
      trading_client=trading,
      edge_client=edge,
      session=session,
    )

  async def sub_account_id(self) -> str:
    """The default trading sub-account, which trading calls use when `sub_account_id` is
    left out: `trading_account_id` when configured, else the one the session's API key is
    scoped to (logging in first if needed).

    Raises:
      AuthError: A public client (built with `public=True`), or a session scoped to no
        sub-account (a funding-account key or a wallet login) with no configured
        `trading_account_id` (the error says how to configure one).
    """
    return await self.trading_client.sub_account_id()

  def shared(self) -> list[Owned]:
    """The three surfaces' clients, each owned once by `async with client`. The session and
    the market-data gateway are owned once more by the transports sharing them."""
    return [self.market_client, self.trading_client, self.edge_client]
