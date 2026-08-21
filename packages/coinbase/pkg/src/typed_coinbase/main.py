"""The Coinbase client root."""

from dataclasses import dataclass
import asyncio

from .core.auth import resolve_credentials
from .core.transport.http import HttpRpcClient
from .core.transport.ws import CoinbaseSocketClient, MARKET_DATA_URL, USER_URL
from .accounts import Accounts
from .advanced_trade import AdvancedTrade
from .market_data import MarketData
from .user import User


@dataclass(kw_only=True)
class Coinbase:
  """Coinbase client: Coinbase App (v2) and Advanced Trade (v3), both REST and
  WebSocket, all authenticated by one CDP API Key.

  Examples:
    ```python
    from typed_coinbase import Coinbase

    async with Coinbase.new() as client:
      accounts = await client.advanced_trade.list_accounts()
    ```
  """

  accounts: Accounts
  """Coinbase App v2 — legacy accounts, transactions, transfers."""
  advanced_trade: AdvancedTrade
  """Advanced Trade v3 — orders, products, portfolios, fees, convert."""
  market_data: MarketData
  """Public WebSocket market data channels."""
  user: User
  """Private WebSocket order and position updates."""

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
        `advanced_trade.list_products` and `market_data` will work.
      validate: Validate responses against their declared schema by default.
    """
    credentials = resolve_credentials(key_name, private_key, public=public)
    http = HttpRpcClient(credentials=credentials, validate=validate)
    return cls(
      accounts=Accounts(client=http),
      advanced_trade=AdvancedTrade(client=http),
      market_data=MarketData(
        client=CoinbaseSocketClient.new(MARKET_DATA_URL, validate=validate)
      ),
      user=User(
        client=CoinbaseSocketClient.new(
          USER_URL, credentials=credentials, validate=validate
        )
      ),
    )

  async def __aenter__(self):
    await asyncio.gather(
      self.accounts.__aenter__(),
      self.advanced_trade.__aenter__(),
      self.market_data.__aenter__(),
      self.user.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.accounts.__aexit__(exc_type, exc_value, traceback),
      self.advanced_trade.__aexit__(exc_type, exc_value, traceback),
      self.market_data.__aexit__(exc_type, exc_value, traceback),
      self.user.__aexit__(exc_type, exc_value, traceback),
    )
