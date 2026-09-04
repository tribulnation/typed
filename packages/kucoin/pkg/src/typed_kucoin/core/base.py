"""KuCoin client root and streams composition bases (design §5c): hand-written classes
holding each heterogeneous child's already-built transport, wrapped by the generated
`KuCoin`/`Streams` composites.

`KuCoin` composes ten REST products, sharing exactly three physical HTTP connections
(one per real base URL Classic products live on -- `api.kucoin.com`, `api-futures.
kucoin.com`, `api-broker.kucoin.com`), and one WebSocket surface (`streams`), sharing
exactly two physical connections (Spot/Margin, Futures) -- so its own resolved `core`
(`KuCoinBase`) is a *Base* holding one field per physical transport, built once in
`.new()`, never a single shared transport every child forwards unchanged (design §5c).

`streams` itself further composes five leaf-bearing groupings that share one of the two
sockets `KuCoinBase` already built -- `StreamsBase` is design §5a's own "extra
caller-supplied value" forwarding mechanism, layered on top of §5c's explicit `children`
mapping (the two mechanisms "answer independent questions" and compose without
conflict, per design §5c's own text).
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .auth import Credentials, resolve_credentials
from .transport.http import BROKER_API_URL, DEFAULT_API_URL, FUTURES_API_URL, HttpRpcClient
from .transport.ws import SocketStreamClient


@dataclass(kw_only=True, frozen=True)
class StreamsBase:
  """The two physical WebSocket connections `Streams` composes: Spot/Margin (also
  serving Margin's own private channels) and Futures -- see `KuCoinBase.new`, which
  builds both."""

  spot_margin_stream_client: SocketStreamClient
  futures_stream_client: SocketStreamClient

  @classmethod
  def new(cls, client: SocketStreamClient, *, futures_stream_client: SocketStreamClient) -> Self:
    """Build from the two already-connected sockets `KuCoinBase.new` constructs.

    Args:
      client: The Spot/Margin connection -- forwarded as `spot_margin_stream_client`.
      futures_stream_client: The Futures connection.
    """
    return cls(spot_margin_stream_client=client, futures_stream_client=futures_stream_client)

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.spot_margin_stream_client.__aenter__(), self.futures_stream_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.spot_margin_stream_client.__aexit__(exc_type, exc_value, traceback),
      self.futures_stream_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True)
class KuCoinBase:
  """KuCoin client root: builds and owns the five physical transports every generated
  composite (`Account`, `Spot`, `Margin`, `Earn`, `VipLending`, `Affiliate`, `Convert`,
  `Futures`, `CopyTrading`, `Broker`, `Streams`) forwards unchanged -- three HTTP
  clients (one per real base URL) and two WebSocket connections (Spot/Margin, Futures).
  """

  default_client: HttpRpcClient
  futures_rest_client: HttpRpcClient
  broker_client: HttpRpcClient
  spot_margin_stream_client: SocketStreamClient
  futures_stream_client: SocketStreamClient

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
    for a credential-free client restricted to public endpoints/channels.

    One `HttpRpcClient` is shared per base URL -- `api.kucoin.com` (Account, Spot,
    Margin, Earn, VIP Lending, Affiliate, Convert), `api-futures.kucoin.com` (Futures,
    Copy Trading) and `api-broker.kucoin.com` (Broker) -- so every product hitting the
    same host shares one connection pool, rather than each opening its own. The two
    WebSocket connections (Spot/Margin, Futures) each open with a **private** bullet
    token whenever credentials are set -- one connection then serves both public and
    private topics -- and a public one otherwise, restricting each connection to public
    topics only.

    Args:
      api_key: KuCoin API key; read from `KUCOIN_API_KEY` when omitted.
      api_secret: KuCoin API secret; read from `KUCOIN_API_SECRET` when omitted.
      api_passphrase: KuCoin API passphrase; read from `KUCOIN_API_PASSPHRASE` when omitted.
      public: Build a credential-free client instead of requiring credentials.
      validate: Validate responses/pushed payloads by default.

    Raises:
      AuthError: `public` is false and any credential was not passed or found in the
        environment.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    credentials = resolve_credentials(api_key, api_secret, api_passphrase, public=public)
    default_client = HttpRpcClient(base_url=DEFAULT_API_URL, credentials=credentials, validate=validate)
    futures_rest_client = HttpRpcClient(
      base_url=FUTURES_API_URL, credentials=credentials, validate=validate
    )
    broker_client = HttpRpcClient(base_url=BROKER_API_URL, credentials=credentials, validate=validate)
    private = credentials is not None
    spot_margin_stream_client = SocketStreamClient.new(
      bullet=default_client, private=private, validate=validate,
    )
    futures_stream_client = SocketStreamClient.new(
      bullet=futures_rest_client, private=private, validate=validate,
    )
    return cls(
      default_client=default_client,
      futures_rest_client=futures_rest_client,
      broker_client=broker_client,
      spot_margin_stream_client=spot_margin_stream_client,
      futures_stream_client=futures_stream_client,
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.default_client.__aenter__(),
      self.futures_rest_client.__aenter__(),
      self.broker_client.__aenter__(),
      self.spot_margin_stream_client.__aenter__(),
      self.futures_stream_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.default_client.__aexit__(exc_type, exc_value, traceback),
      self.futures_rest_client.__aexit__(exc_type, exc_value, traceback),
      self.broker_client.__aexit__(exc_type, exc_value, traceback),
      self.spot_margin_stream_client.__aexit__(exc_type, exc_value, traceback),
      self.futures_stream_client.__aexit__(exc_type, exc_value, traceback),
    )
