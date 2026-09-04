"""Coinbase client root composition (design §5c): a hand-written `Base` holding every
transport this client ultimately needs, built once in `.new()`, wrapped by the generated
`Coinbase` composite.

`Coinbase` composes two structurally independent children -- `app` (Coinbase App /
Advanced Trade, one CDP API Key) and `exchange` (Coinbase Exchange, a separate HMAC key) --
so its own resolved core (`CoinbaseBase`) is a *Base* holding one field per child's own
transport(s), not a single shared transport every child forwards unchanged (design §5c).
`app` itself further composes `accounts`/`advanced_trade.http` (one shared HTTP transport)
and `advanced_trade.streams` (two further WebSocket connections) -- see
`typed_coinbase.app.core.AppBase` and `typed_coinbase.app.advanced_trade.core.
AdvancedTradeBase` for that deeper split.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .auth import resolve_credentials
from .transport.http import HttpRpcClient
from .transport.ws import CoinbaseSocketClient, MARKET_DATA_URL, USER_URL
from ..exchange.core.auth import resolve_credentials as resolve_exchange_credentials
from ..exchange.core.transport.http import ExchangeHttpRpcClient
from ..exchange.core.transport.ws import ExchangeSocketClient


@dataclass(kw_only=True)
class CoinbaseBase:
  """Coinbase client root: builds and owns every physical transport the generated
  composite tree forwards unchanged -- one HTTP client and two WebSocket connections for
  Coinbase App, plus Coinbase Exchange's own separate HTTP client and WebSocket Feed
  connection."""

  app_client: HttpRpcClient
  market_client: CoinbaseSocketClient
  user_client: CoinbaseSocketClient
  exchange_client: ExchangeHttpRpcClient
  feed_client: ExchangeSocketClient

  @classmethod
  def new(
    cls,
    *,
    key_name: str | None = None,
    private_key: str | None = None,
    public: bool = False,
    exchange_key: str | None = None,
    exchange_secret: str | None = None,
    exchange_passphrase: str | None = None,
    exchange_public: bool = True,
    validate: bool = True,
  ) -> Self:
    """Build a Coinbase client.

    Args:
      key_name: CDP API Key name (`organizations/.../apiKeys/...`); read from
        `COINBASE_API_KEY_NAME` when omitted.
      private_key: CDP API Key private key (Ed25519, base64; or an EC PEM key); read
        from `COINBASE_PRIVATE_KEY` when omitted.
      public: Skip CDP credential resolution and build `app` public-only -- only
        `app.advanced_trade.http.products.public.list` and
        `app.advanced_trade.streams.market_data` will work.
      exchange_key: Coinbase Exchange API key; read from `COINBASE_EXCHANGE_API_KEY` when
        omitted.
      exchange_secret: Coinbase Exchange API secret; read from
        `COINBASE_EXCHANGE_API_SECRET` when omitted.
      exchange_passphrase: Coinbase Exchange API passphrase; read from
        `COINBASE_EXCHANGE_PASSPHRASE` when omitted.
      exchange_public: Skip Exchange credential resolution and build `exchange`
        public-only -- only `exchange.http.products.list` and
        `exchange.streams.heartbeat` will work. Defaults to `True`, unlike `public`
        above: no `[policy]` yet approves an authenticated Exchange call (see
        `client.toml`), so building an authenticated `exchange` needs this explicitly
        set to `False` in addition to real credentials.
      validate: Validate responses against their declared schema by default.
    """
    credentials = resolve_credentials(key_name, private_key, public=public)
    exchange_credentials = resolve_exchange_credentials(
      exchange_key, exchange_secret, exchange_passphrase, public=exchange_public
    )
    return cls(
      app_client=HttpRpcClient(credentials=credentials, validate=validate),
      market_client=CoinbaseSocketClient.new(MARKET_DATA_URL, validate=validate),
      user_client=CoinbaseSocketClient.new(
        USER_URL, credentials=credentials, validate=validate
      ),
      exchange_client=ExchangeHttpRpcClient(credentials=exchange_credentials, validate=validate),
      feed_client=ExchangeSocketClient.new(credentials=exchange_credentials, validate=validate),
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.app_client.__aenter__(),
      self.market_client.__aenter__(),
      self.user_client.__aenter__(),
      self.exchange_client.__aenter__(),
      self.feed_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.app_client.__aexit__(exc_type, exc_value, traceback),
      self.market_client.__aexit__(exc_type, exc_value, traceback),
      self.user_client.__aexit__(exc_type, exc_value, traceback),
      self.exchange_client.__aexit__(exc_type, exc_value, traceback),
      self.feed_client.__aexit__(exc_type, exc_value, traceback),
    )
