"""`ClientBase`: what the `Nado` root inherits — network and credential resolution, and the
transports every surface is composed over.

The root is the only owner of every transport: entering it opens nothing (the HTTP pool and
both sockets connect lazily, on first use) and leaving it closes them all.
"""

from typing_extensions import Self
from dataclasses import dataclass
from datetime import timedelta
import asyncio

from typed_core.http import HttpClient
from typed_core.ws import Socket

from .auth import Credentials, resolve_credentials
from .exc import BadRequest
from .networks import NETWORKS, Network, NetworkProfile
from .signing import DEFAULT_RECV_WINDOW, Signer
from .transport.engine import EngineTransport
from .transport.indexer import IndexerTransport
from .transport.rest import RestTransport
from .transport.subscriptions import SubscriptionsSocket, SubscriptionsTransport
from .transport.ws import GATEWAY_MAX_SIZE, GatewaySocket


@dataclass(kw_only=True)
class ClientBase:
  """Network, credentials and the transports of one Nado client.

  Every REST service shares one HTTP connection pool; the gateway and the subscriptions
  each hold one WebSocket. `async with client:` closes all of them on exit.
  """

  network: NetworkProfile
  """Hosts and signing domain of the deployment this client talks to."""
  credentials: Credentials | None
  """Signing key and default subaccount; `None` for a public client."""
  http: HttpClient
  """The shared HTTP connection pool."""
  gateway_client: EngineTransport
  """Gateway queries, edge queries and executes, over REST or WebSocket v1."""
  trigger_client: EngineTransport
  """Trigger service: conditional and TWAP orders, REST only."""
  archive_client: IndexerTransport
  """Archive (indexer) v1: historical data."""
  rewards_client: IndexerTransport
  """Rewards v1: airdrops and leaderboards."""
  gateway_v2_client: RestTransport
  """Gateway REST v2: market data in aggregator-style shapes."""
  archive_v2_client: RestTransport
  """Archive REST v2: market data in aggregator-style shapes."""
  streams_client: SubscriptionsTransport
  """Subscriptions WebSocket."""

  @classmethod
  def new(
    cls,
    *,
    network: Network | NetworkProfile = 'mainnet',
    private_key: str | None = None,
    address: str | None = None,
    subaccount: str | None = None,
    public: bool = False,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    archive_timeout: timedelta = timedelta(seconds=30),
    recv_window: timedelta = DEFAULT_RECV_WINDOW,
  ) -> Self:
    """Build a client: signing (a key: every surface) or `public=True` (every read).

    Nado has no API keys: reads are public, even per-subaccount ones, and every write is an
    EIP-712 signature. Arguments fall back to environment variables, prefixed `NADO_` on
    mainnet and `NADO_TESTNET_` on testnet.

    Args:
      network: Deployment: `mainnet` (Ink) or `testnet` (Ink Sepolia), or a custom
        `NetworkProfile` (a local mock server, say).
      private_key: Signing key, hex: the subaccount owner's, or its linked signer's
        (`NADO_PRIVATE_KEY`).
      address: Owner wallet of the subaccount, needed when the key is a linked signer
        (`NADO_ADDRESS`); defaults to the key's own address.
      subaccount: Subaccount name (`NADO_SUBACCOUNT`); defaults to `default`.
      public: Skip credentials entirely: reads only.
      validate: Validate responses by default.
      timeout: Bound on each HTTP request, each WebSocket handshake and each socket reply.
      archive_timeout: Bound on each archive (indexer) request instead: its heavier queries
        (a busy subaccount's orders, filtered positions) can take over 10 s.
      recv_window: How far ahead generated deadlines sit: an order nonce's discard time,
        `recvTime`, authentication expirations. At most 100 s.

    Raises:
      AuthError: No signing key was found (and `public` is false), or it is invalid.
      BadRequest: `network` is not a known deployment, or the address or subaccount name is
        invalid.
    """
    if isinstance(network, NetworkProfile):
      profile = network
    elif network in NETWORKS:
      profile = NETWORKS[network]
    else:
      raise BadRequest(
        f'Unknown network {network!r}: one of {", ".join(map(repr, NETWORKS))}'
      )
    credentials = resolve_credentials(
      profile,
      private_key=private_key,
      address=address,
      subaccount=subaccount,
      public=public,
    )
    signer = (
      Signer(
        credentials=credentials,
        chain_id=profile.chain_id,
        endpoint_address=profile.endpoint_address,
        recv_window=recv_window,
      )
      if credentials is not None
      else None
    )
    http = HttpClient(timeout=timeout.total_seconds())
    return cls(
      network=profile,
      credentials=credentials,
      http=http,
      gateway_client=EngineTransport(
        http=http,
        base_url=profile.gateway_url,
        socket=GatewaySocket(
          profile.gateway_ws_url,
          timeout=timeout,
          reply_timeout=timeout,
          max_size=GATEWAY_MAX_SIZE,
        ),
        signer=signer,
        validate=validate,
      ),
      trigger_client=EngineTransport(
        http=http, base_url=profile.trigger_url, signer=signer, validate=validate
      ),
      archive_client=IndexerTransport(
        http=http,
        url=profile.archive_url,
        signer=signer,
        validate=validate,
        timeout=archive_timeout.total_seconds(),
      ),
      rewards_client=IndexerTransport(
        http=http, url=profile.rewards_url, signer=signer, validate=validate
      ),
      gateway_v2_client=RestTransport(
        http=http, base_url=profile.gateway_v2_url, validate=validate
      ),
      archive_v2_client=RestTransport(
        http=http, base_url=profile.archive_v2_url, validate=validate
      ),
      streams_client=SubscriptionsTransport(
        socket=SubscriptionsSocket(
          profile.subscriptions_url,
          timeout=timeout,
          reply_timeout=timeout,
          signer=signer,
        ),
        validate=validate,
      ),
    )

  async def __aenter__(self) -> Self:
    """Take ownership of every transport. Nothing connects yet."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close both sockets, if open, and the HTTP connection pool."""
    sockets: list[Socket] = [self.streams_client.socket]
    if self.gateway_client.socket is not None:
      sockets.append(self.gateway_client.socket)
    try:
      await asyncio.gather(
        *(socket.__aexit__(exc_type, exc_value, traceback) for socket in sockets)
      )
    finally:
      await self.http.__aexit__(exc_type, exc_value, traceback)
