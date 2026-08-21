"""The Deribit client root."""

from typing_extensions import Literal, Self
from dataclasses import dataclass
from functools import cached_property
import asyncio

from .account import Account
from .auth import AuthRouter
from .block_rfq import BlockRfq
from .block_trade import BlockTrade
from .combo_books import ComboBooks
from .core.auth import Credentials, resolve_credentials
from .core.endpoint.rpc import RpcEndpoint
from .core.transport.http import (
  HmacHttpRpcClient,
  OAuthHttpRpcClient,
  resolve_http_base_url,
)
from .core.transport.ws import SocketRpcStreamClient, resolve_ws_url
from .market_data import MarketData
from .matching_engine import MatchingEngine
from .session import Session
from .streams import Streams
from .subscription_management import SubscriptionManagement
from .supporting import Supporting
from .trading import Trading
from .wallet import Wallet

HttpAuth = Literal['token', 'hmac']


@dataclass(kw_only=True, frozen=True)
class Rpc(RpcEndpoint):
  """Deribit's request/reply method surface: `market_data`, `trading`, `account`, ...

  Reached through `Deribit.http` or `Deribit.ws` — see `Deribit` for the difference.
  """

  @cached_property
  def market_data(self) -> MarketData:
    return MarketData(client=self.client)

  @cached_property
  def trading(self) -> Trading:
    return Trading(client=self.client)

  @cached_property
  def account(self) -> Account:
    return Account(client=self.client)

  @cached_property
  def auth(self) -> AuthRouter:
    return AuthRouter(client=self.client)

  @cached_property
  def block_rfq(self) -> BlockRfq:
    return BlockRfq(client=self.client)

  @cached_property
  def block_trade(self) -> BlockTrade:
    return BlockTrade(client=self.client)

  @cached_property
  def combo_books(self) -> ComboBooks:
    return ComboBooks(client=self.client)

  @cached_property
  def matching_engine(self) -> MatchingEngine:
    return MatchingEngine(client=self.client)

  @cached_property
  def session(self) -> Session:
    return Session(client=self.client)

  @cached_property
  def subscription_management(self) -> SubscriptionManagement:
    return SubscriptionManagement(client=self.client)

  @cached_property
  def supporting(self) -> Supporting:
    return Supporting(client=self.client)

  @cached_property
  def wallet(self) -> Wallet:
    return Wallet(client=self.client)


@dataclass(kw_only=True, frozen=True)
class Deribit:
  """Deribit client.

  `market_data`, `trading`, `account`, ... are reachable over two transports:

  - `.http` — request/reply over HTTP.
  - `.ws` — the same methods over WebSocket, plus a handful Deribit only serves this way
    (`trading.mass_quote`, `session.set_heartbeat`, ...).
  - `.streams` — channel subscriptions, always WebSocket.

  Each connects on first use, not at construction.

  Examples:
    ```python
    from typed_deribit import Deribit

    async with Deribit.new(testnet=True) as client:
      instruments = await client.http.market_data.get_instruments(
        currency='BTC', kind='future'
      )
      print(instruments)
    ```
  """

  credentials: Credentials | None
  testnet: bool
  http_auth: HttpAuth = 'token'
  validate: bool = True

  @cached_property
  def http(self) -> Rpc:
    base_url = resolve_http_base_url(self.testnet)
    client = (
      HmacHttpRpcClient(
        base_url=base_url, credentials=self.credentials, validate=self.validate
      )
      if self.http_auth == 'hmac'
      else OAuthHttpRpcClient(
        base_url=base_url, credentials=self.credentials, validate=self.validate
      )
    )
    return Rpc(client=client)

  @cached_property
  def ws(self) -> Rpc:
    ws_url = resolve_ws_url(self.testnet)
    client = SocketRpcStreamClient.new(
      ws_url, credentials=self.credentials, validate=self.validate
    )
    return Rpc(client=client)

  @cached_property
  def streams(self) -> Streams:
    ws_url = resolve_ws_url(self.testnet)
    client = SocketRpcStreamClient.new(
      ws_url, credentials=self.credentials, validate=self.validate
    )
    return Streams(client=client)

  @classmethod
  def new(
    cls,
    *,
    client_id: str | None = None,
    client_secret: str | None = None,
    public: bool = False,
    testnet: bool = False,
    http_auth: HttpAuth = 'token',
    validate: bool = True,
  ) -> Self:
    """Create a Deribit client. Connects nothing yet -- see `.http`/`.ws`/`.streams`.

    Args:
      client_id: Deribit API client id; read from `{TEST_,}DERIBIT_CLIENT_ID` when
        omitted (prefix picked by `testnet`).
      client_secret: Deribit API client secret; read from `{TEST_,}DERIBIT_CLIENT_SECRET`
        when omitted.
      public: Build a credential-free client instead of requiring one.
      testnet: Target `test.deribit.com` (HTTP) / `wss://test.deribit.com` (WS) instead
        of the mainnet hosts, and read the `TEST_`-prefixed environment variables.
      http_auth: `.http`'s authentication scheme. `'token'` (default) exchanges
        `client_id`/`client_secret` for a Bearer token via `public/auth`, cached and
        refreshed automatically. `'hmac'` signs every request individually instead
        (Deribit's `client_signature` grant) — see `core.auth`. `.ws` and `.streams`
        always use token auth; `http_auth` has no effect on them.
      validate: Validate responses by default, on every surface.

    Raises:
      AuthError: `public` is false and no credentials were passed or found in the
        environment.

    References:
      - [Deribit API docs](https://docs.deribit.com/)
    """
    credentials = resolve_credentials(
      client_id, client_secret, public=public, testnet=testnet
    )
    return cls(
      credentials=credentials, testnet=testnet, http_auth=http_auth, validate=validate
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.http.__aenter__(), self.ws.__aenter__(), self.streams.__aenter__()
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http.__aexit__(exc_type, exc_value, traceback),
      self.ws.__aexit__(exc_type, exc_value, traceback),
      self.streams.__aexit__(exc_type, exc_value, traceback),
    )
