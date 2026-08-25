"""The Coinbase client root."""

from dataclasses import dataclass

from .core.auth import resolve_credentials
from .core.transport.http import HttpRpcClient
from .core.transport.ws import CoinbaseSocketClient, MARKET_DATA_URL, USER_URL
from .app import App


@dataclass(kw_only=True)
class Coinbase:
  """Coinbase client: the Coinbase App (Consumer APIs) tier, authenticated by one CDP API
  Key. See `app`'s own `References:` for the upstream docs it maps to.

  Examples:
    ```python
    from typed_coinbase import Coinbase

    async with Coinbase.new() as client:
      accounts = await client.app.advanced_trade.http.accounts.list()
    ```
  """

  app: App
  """Coinbase App (Consumer APIs) — the only tier this client implements.

  References:
    - [Coinbase App API docs](https://docs.cdp.coinbase.com/coinbase-app/docs/welcome)
  """

  @classmethod
  def new(
    cls,
    *,
    key_name: str | None = None,
    private_key: str | None = None,
    public: bool = False,
    validate: bool = True,
  ):
    """Build a Coinbase client.

    Args:
      key_name: CDP API Key name (`organizations/.../apiKeys/...`); read from
        `COINBASE_API_KEY_NAME` when omitted.
      private_key: CDP API Key private key (Ed25519, base64; or an EC PEM key); read
        from `COINBASE_PRIVATE_KEY` when omitted.
      public: Skip credential resolution and build a public-only client — only
        `app.advanced_trade.http.products.public.list` and `app.advanced_trade.streams.market_data`
        will work.
      validate: Validate responses against their declared schema by default.
    """
    credentials = resolve_credentials(key_name, private_key, public=public)
    http = HttpRpcClient(credentials=credentials, validate=validate)
    return cls(
      app=App.new(
        http=http,
        market_data=CoinbaseSocketClient.new(MARKET_DATA_URL, validate=validate),
        user=CoinbaseSocketClient.new(
          USER_URL, credentials=credentials, validate=validate
        ),
      )
    )

  async def __aenter__(self) -> 'Coinbase':
    await self.app.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.app.__aexit__(exc_type, exc_value, traceback)
