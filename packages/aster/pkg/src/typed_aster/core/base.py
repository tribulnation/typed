"""Hand-written construction of every transport, and the bases the composed client
classes subclass.

Each trading surface (futures, spot, prediction) owns three transports — REST, market
streams and the user-data stream — Aster Chain owns two — REST and JSON-RPC — and BAPI,
the web backend's public API, owns one. They are built once here, from resolved
credentials and the selected network, and forwarded field by field: a surface's REST
routers take `client`, its `streams` child takes `streams_client`, its `user_stream`
child takes `user_stream_client`, Aster Chain's `rpc` child takes `rpc_client`, and
`bapi` takes `bapi_client`.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .auth import Credentials, Wallet, resolve_credentials
from .transport.bapi import BapiClient
from .transport.http import HttpRpcClient
from .transport.jsonrpc import HttpJsonRpcClient
from .transport.ws.streams import SocketStreamClient
from .transport.ws.user_stream import UserStreamSocketClient
from .urls import (
  CHAIN_REST_URL,
  CHAIN_RPC_URL,
  Surface,
  rest_url,
  streams_url,
  user_stream_url,
)


@dataclass(kw_only=True, frozen=True)
class SurfaceClients:
  """One trading surface's transports: REST, market streams and the user-data stream."""

  client: HttpRpcClient
  streams_client: SocketStreamClient
  user_stream_client: UserStreamSocketClient

  @classmethod
  def build(
    cls,
    surface: Surface,
    *,
    credentials: Credentials | None,
    mainnet: bool,
    validate: bool,
  ) -> Self:
    """Build the transports of `surface` for one network."""
    return cls(
      client=HttpRpcClient(
        base_url=rest_url(surface, mainnet=mainnet),
        credentials=credentials,
        mainnet=mainnet,
        validate=validate,
      ),
      streams_client=SocketStreamClient.new(
        streams_url(surface, mainnet=mainnet), validate=validate
      ),
      user_stream_client=UserStreamSocketClient(
        base_url=user_stream_url(surface, mainnet=mainnet), validate=validate
      ),
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.client.__aenter__(),
      self.streams_client.__aenter__(),
      self.user_stream_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.client.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
      self.user_stream_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class SurfaceBase(SurfaceClients):
  """Base of the futures, spot and prediction composites: REST routers sit directly on
  it (forwarding `client`), beside `streams` and `user_stream`."""

  @classmethod
  def new(cls, client: SurfaceClients) -> Self:
    """Unpack already-built transports into this base."""
    return cls(
      client=client.client,
      streams_client=client.streams_client,
      user_stream_client=client.user_stream_client,
    )


@dataclass(kw_only=True, frozen=True)
class ChainClients:
  """Aster Chain's transports: REST and JSON-RPC. Both are mainnet only."""

  client: HttpRpcClient
  rpc_client: HttpJsonRpcClient

  @classmethod
  def build(cls, *, credentials: Credentials | None, validate: bool) -> Self:
    """Build the Aster Chain transports. Signed calls always sign for mainnet."""
    return cls(
      client=HttpRpcClient(
        base_url=CHAIN_REST_URL,
        credentials=credentials,
        mainnet=True,
        validate=validate,
      ),
      rpc_client=HttpJsonRpcClient(url=CHAIN_RPC_URL, validate=validate),
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.client.__aenter__(), self.rpc_client.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.client.__aexit__(exc_type, exc_value, traceback),
      self.rpc_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class ChainBase(ChainClients):
  """Base of the Aster Chain composite: REST routers sit directly on it (forwarding
  `client`), beside `rpc`."""

  @classmethod
  def new(cls, client: ChainClients) -> Self:
    """Unpack already-built transports into this base."""
    return cls(client=client.client, rpc_client=client.rpc_client)


@dataclass(kw_only=True, frozen=True)
class AsterBase:
  """Base of the `Aster` root: every surface's transports, built once in `.new()`."""

  futures_clients: SurfaceClients
  spot_clients: SurfaceClients
  prediction_clients: SurfaceClients
  chain_clients: ChainClients
  bapi_client: BapiClient

  @classmethod
  def new(
    cls,
    *,
    user: str | None = None,
    signer: Wallet | None = None,
    main: Wallet | None = None,
    public: bool = False,
    mainnet: bool = True,
    validate: bool = True,
  ) -> Self:
    """Create an Aster client.

    Arguments win; missing ones are read from `ASTER_USER`,
    `ASTER_SIGNER_PRIVATE_KEY` and `ASTER_USER_PRIVATE_KEY`.

    Args:
      user: The main wallet address (the Aster account). Defaults to `main`'s address.
      signer: The API wallet (agent) private key, which signs trading and account calls.
      main: The main wallet private key. Only needed for agent/builder/sub-account
        management, Aster Chain transfers and staking, and withdrawals.
      public: Build a client for public calls only, reading no credentials.
      mainnet: Use mainnet when true, testnet when false. Aster Chain has no testnet:
        with `mainnet=False` it serves public calls only. BAPI has none either, and
        always calls mainnet.
      validate: Validate responses by default.

    Raises:
      AuthError: No usable credentials, or they are inconsistent.
    """
    credentials = resolve_credentials(
      user=user, signer=signer, main=main, public=public
    )

    def surface(name: Surface) -> SurfaceClients:
      return SurfaceClients.build(
        name, credentials=credentials, mainnet=mainnet, validate=validate
      )

    return cls(
      futures_clients=surface('futures'),
      spot_clients=surface('spot'),
      prediction_clients=surface('prediction'),
      chain_clients=ChainClients.build(
        credentials=credentials if mainnet else None, validate=validate
      ),
      bapi_client=BapiClient(validate=validate),
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.futures_clients.__aenter__(),
      self.spot_clients.__aenter__(),
      self.prediction_clients.__aenter__(),
      self.chain_clients.__aenter__(),
      self.bapi_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.futures_clients.__aexit__(exc_type, exc_value, traceback),
      self.spot_clients.__aexit__(exc_type, exc_value, traceback),
      self.prediction_clients.__aexit__(exc_type, exc_value, traceback),
      self.chain_clients.__aexit__(exc_type, exc_value, traceback),
      self.bapi_client.__aexit__(exc_type, exc_value, traceback),
    )
