"""KuCoin client root and streams composition bases (design §5c): hand-written classes
holding each heterogeneous child's already-built transport, wrapped by the generated
`KuCoin`/`Streams` composites.

`KuCoin` composes eleven REST products (the Classic ten plus `uta`, the Unified Trading
Account API on `api.kucoin.com`), sharing exactly three physical HTTP connections
(one per base URL -- `api.kucoin.com`, `api-futures.kucoin.com`,
`api-broker.kucoin.com`), and one WebSocket surface (`streams`), sharing exactly three
physical connections (Classic Spot/Margin, Classic Futures, UTA private) -- so its own resolved `core`
(`KuCoinBase`) is a *Base* holding one field per physical transport, built once in
`.new()`, never a single shared transport every child forwards unchanged (design §5c).

`streams` itself further composes six leaf-bearing groupings that share one of the three
sockets `KuCoinBase` already built -- `StreamsBase` is design §5a's own "extra
caller-supplied value" forwarding mechanism, layered on top of §5c's explicit `children`
mapping (the two mechanisms "answer independent questions" and compose without
conflict, per design §5c's own text).
"""

from typing_extensions import Self
from typed_core.http import HttpClient

from dataclasses import dataclass
from contextlib import AsyncExitStack

from .auth import Credentials, resolve_credentials
from .transport.http import (
  BROKER_API_URL,
  DEFAULT_API_URL,
  FUTURES_API_URL,
  HttpRpcClient,
)
from .transport.uta_ws import UtaStreamClient
from .transport.ws import SocketStreamClient


@dataclass(kw_only=True, frozen=True)
class StreamsBase:
  """The three physical WebSocket connections `Streams` composes: Classic Spot/Margin
  (also serving Margin's own private channels), Classic Futures, and the Unified Trading
  Account's private connection -- see `KuCoinBase.new`, which builds all three."""

  spot_margin_stream_client: SocketStreamClient
  futures_stream_client: SocketStreamClient
  uta_private_stream_client: UtaStreamClient

  @classmethod
  def new(
    cls,
    client: SocketStreamClient,
    *,
    futures_stream_client: SocketStreamClient,
    uta_private_stream_client: UtaStreamClient,
  ) -> Self:
    """Build from the three already-built connections `KuCoinBase.new` constructs.

    Args:
      client: The Spot/Margin connection -- forwarded as `spot_margin_stream_client`.
      futures_stream_client: The Futures connection.
      uta_private_stream_client: The UTA private connection.
    """
    return cls(
      spot_margin_stream_client=client,
      futures_stream_client=futures_stream_client,
      uta_private_stream_client=uta_private_stream_client,
    )

  async def __aenter__(self) -> Self:
    """Roll back earlier streams when entry fails or is cancelled."""
    async with AsyncExitStack() as stack:
      await stack.enter_async_context(self.spot_margin_stream_client)
      await stack.enter_async_context(self.futures_stream_client)
      await stack.enter_async_context(self.uta_private_stream_client)
      stack.pop_all()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Attempt every stream exit before propagating a cleanup failure."""
    stack = AsyncExitStack()
    stack.push_async_exit(self.spot_margin_stream_client)
    stack.push_async_exit(self.futures_stream_client)
    stack.push_async_exit(self.uta_private_stream_client)
    await stack.__aexit__(exc_type, exc_value, traceback)


@dataclass(kw_only=True)
class KuCoinBase:
  """KuCoin client root: builds and owns the six physical transports every generated
  composite (`Account`, `Spot`, `Margin`, `Earn`, `VipLending`, `Affiliate`, `Convert`,
  `Futures`, `CopyTrading`, `Broker`, `Uta`, `Streams`) forwards unchanged -- three HTTP
  clients (one per real base URL) and three WebSocket connections (Classic Spot/Margin,
  Classic Futures, UTA private).
  """

  default_client: HttpRpcClient
  futures_rest_client: HttpRpcClient
  broker_client: HttpRpcClient
  spot_margin_stream_client: SocketStreamClient
  futures_stream_client: SocketStreamClient
  uta_private_stream_client: UtaStreamClient

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    api_secret: str | None = None,
    api_passphrase: str | None = None,
    public: bool = False,
    validate: bool = True,
    http: HttpClient | None = None,
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
      http: HTTP transport override; closed when this client exits.

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
      http=http if http is not None else HttpClient(),
      base_url=DEFAULT_API_URL,
      credentials=credentials,
      validate=validate,
    )
    futures_rest_client = HttpRpcClient(
      http=http if http is not None else HttpClient(),
      base_url=FUTURES_API_URL,
      credentials=credentials,
      validate=validate,
    )
    broker_client = HttpRpcClient(
      http=http if http is not None else HttpClient(),
      base_url=BROKER_API_URL,
      credentials=credentials,
      validate=validate,
    )
    private = credentials is not None
    spot_margin_stream_client = SocketStreamClient.new(
      bullet=default_client,
      private=private,
      validate=validate,
    )
    futures_stream_client = SocketStreamClient.new(
      bullet=futures_rest_client,
      private=private,
      validate=validate,
    )
    uta_private_stream_client = UtaStreamClient.new(
      credentials=credentials, validate=validate
    )
    return cls(
      default_client=default_client,
      futures_rest_client=futures_rest_client,
      broker_client=broker_client,
      spot_margin_stream_client=spot_margin_stream_client,
      futures_stream_client=futures_stream_client,
      uta_private_stream_client=uta_private_stream_client,
    )

  async def __aenter__(self) -> Self:
    """Acquire dependencies first, rolling back on failed or cancelled entry."""
    async with AsyncExitStack() as stack:
      await stack.enter_async_context(self.default_client)
      await stack.enter_async_context(self.futures_rest_client)
      await stack.enter_async_context(self.broker_client)
      await stack.enter_async_context(self.spot_margin_stream_client)
      await stack.enter_async_context(self.futures_stream_client)
      await stack.enter_async_context(self.uta_private_stream_client)
      stack.pop_all()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close dependent sockets before HTTP and attempt every transport exit."""
    stack = AsyncExitStack()
    stack.push_async_exit(self.default_client)
    stack.push_async_exit(self.futures_rest_client)
    stack.push_async_exit(self.broker_client)
    stack.push_async_exit(self.spot_margin_stream_client)
    stack.push_async_exit(self.futures_stream_client)
    stack.push_async_exit(self.uta_private_stream_client)
    await stack.__aexit__(exc_type, exc_value, traceback)
