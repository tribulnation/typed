"""The KuCoin client root."""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .core import (
  BROKER_API_URL,
  DEFAULT_API_URL,
  FUTURES_API_URL,
  HttpRpcClient,
  resolve_credentials,
)
from .account import Account
from .affiliate import Affiliate
from .broker import Broker
from .convert import Convert
from .copy_trading import CopyTrading
from .earn import Earn
from .futures import Futures
from .margin import Margin
from .spot import Spot
from .streams import Streams
from .vip_lending import VipLending


@dataclass(kw_only=True)
class KuCoin:
  """KuCoin client.

  Reaches every REST product under its own field (`client.spot.server_time()`,
  `client.account.user_info()`, ...) and every WebSocket connection under `streams`
  (`client.streams.spot_margin.ticker(...)` for public topics, `.balance(...)` for
  private ones — one connection serves both) from one object. Nothing connects until
  it's actually used, and closing the client only tears down the connections that were
  actually opened.

  Examples:
    ```python
    from typed_kucoin import KuCoin

    async with KuCoin.new(public=True) as client:
      now = await client.spot.server_time()
    ```
  """

  account: Account
  spot: Spot
  margin: Margin
  earn: Earn
  vip_lending: VipLending
  affiliate: Affiliate
  convert: Convert
  futures: Futures
  copy_trading: CopyTrading
  broker: Broker
  streams: Streams

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    api_secret: str | None = None,
    api_passphrase: str | None = None,
    public: bool = False,
    validate: bool = True,
  ) -> Self:
    """Create a KuCoin client.

    Defaults to authenticated: `api_key`/`api_secret`/`api_passphrase` fall back to the
    `KUCOIN_API_KEY`/`KUCOIN_API_SECRET`/`KUCOIN_API_PASSPHRASE` environment variables
    when not passed, and it is an error to build one with any missing. Pass `public=True`
    for a credential-free client restricted to public endpoints.

    One `HttpRpcClient` is shared per base URL — `api.kucoin.com` (Account, Spot, Margin,
    Earn, VIP Lending, Affiliate, Convert), `api-futures.kucoin.com` (Futures, Copy
    Trading) and `api-broker.kucoin.com` (Broker) — so every product hitting the same
    host shares one connection pool, rather than each opening its own.

    Args:
      api_key: KuCoin API key; read from `KUCOIN_API_KEY` when omitted.
      api_secret: KuCoin API secret; read from `KUCOIN_API_SECRET` when omitted.
      api_passphrase: KuCoin API passphrase; read from `KUCOIN_API_PASSPHRASE` when omitted.
      public: Build a credential-free client instead of requiring credentials.
      validate: Validate responses by default.

    Raises:
      AuthError: `public` is false and any credential was not passed or found in the
        environment.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    credentials = resolve_credentials(
      api_key, api_secret, api_passphrase, public=public
    )
    default_client = HttpRpcClient(
      base_url=DEFAULT_API_URL, credentials=credentials, validate=validate
    )
    futures_client = HttpRpcClient(
      base_url=FUTURES_API_URL, credentials=credentials, validate=validate
    )
    broker_client = HttpRpcClient(
      base_url=BROKER_API_URL, credentials=credentials, validate=validate
    )
    return cls(
      account=Account(client=default_client),
      spot=Spot(client=default_client),
      margin=Margin(client=default_client),
      earn=Earn(client=default_client),
      vip_lending=VipLending(client=default_client),
      affiliate=Affiliate(client=default_client),
      convert=Convert(client=default_client),
      futures=Futures(client=futures_client),
      copy_trading=CopyTrading(client=futures_client),
      broker=Broker(client=broker_client),
      streams=Streams.new(credentials=credentials, validate=validate),
    )

  def _rest_products(self):
    return (
      self.account,
      self.spot,
      self.margin,
      self.earn,
      self.vip_lending,
      self.affiliate,
      self.convert,
      self.futures,
      self.copy_trading,
      self.broker,
    )

  async def __aenter__(self):
    await asyncio.gather(
      *(product.__aenter__() for product in self._rest_products()),
      self.streams.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      *(
        product.__aexit__(exc_type, exc_value, traceback)
        for product in self._rest_products()
      ),
      self.streams.__aexit__(exc_type, exc_value, traceback),
    )
