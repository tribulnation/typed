"""The Kraken client root."""

from dataclasses import dataclass
import asyncio

from .core.auth import TokenCache, resolve_credentials
from .core.transport.http import SPOT_API_URL, HttpRpcClient
from .core.transport.ws import SPOT_WS_AUTH_URL, SPOT_WS_URL, KrakenSocketClient
from .spot import Spot
from .streams import Streams
from .trading_ws import TradingWs


@dataclass(kw_only=True)
class Kraken:
  """Kraken Spot client -- REST and WebSocket v2.

  `streams` is subscriptions only; `trading_ws`'s WS trading methods (`add_order`,
  `cancel_order`, ...) are plain request/reply calls, `await`ed directly rather than
  iterated -- kept off `streams` so its shape stays uniform. Both `streams.private` and
  `trading_ws` reach Kraken over the same authenticated connection.

  Examples:
    ```python
    from typed_kraken import Kraken

    async with Kraken.new() as client:
      ticker = await client.spot.market_data.ticker('XBTUSD')
      print(ticker)
    ```
  """

  spot: Spot
  streams: Streams
  trading_ws: TradingWs

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    private_key: str | None = None,
    public: bool = False,
    validate: bool = True,
  ):
    """Build a Kraken Spot client.

    Args:
      api_key: Kraken API key; read from `KRAKEN_API_KEY` when omitted.
      private_key: Kraken private key; read from `KRAKEN_PRIVATE_KEY` when omitted.
      public: Build a credential-free client, usable only for public endpoints/channels.
      validate: Validate responses by default.
    """
    credentials = resolve_credentials(api_key, private_key, public=public)
    http = HttpRpcClient(
      base_url=SPOT_API_URL, credentials=credentials, validate=validate
    )
    market_client = KrakenSocketClient.new(SPOT_WS_URL, validate=validate)
    private_client = KrakenSocketClient.new(
      SPOT_WS_AUTH_URL,
      token_cache=TokenCache() if credentials is not None else None,
      fetch_token=http.get_ws_token if credentials is not None else None,
      validate=validate,
    )
    return cls(
      spot=Spot(client=http),
      streams=Streams(market_client=market_client, private_client=private_client),
      trading_ws=TradingWs(client=private_client),
    )

  async def __aenter__(self):
    await asyncio.gather(
      self.spot.__aenter__(), self.streams.__aenter__(), self.trading_ws.__aenter__()
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.spot.__aexit__(exc_type, exc_value, traceback),
      self.streams.__aexit__(exc_type, exc_value, traceback),
      self.trading_ws.__aexit__(exc_type, exc_value, traceback),
    )
