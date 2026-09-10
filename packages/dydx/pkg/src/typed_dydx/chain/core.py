"""dYdX Chain client (design §2/§5/§5c/§6, 2026-08-31 codegen mechanization).

`GrpcClient`/`GrpcEndpoint`/`wrap_exceptions` are promoted to `typed_core.grpc` (design
doc §9); re-exported here for every gRPC leaf's own generated import
(`from typed_dydx.chain.core import GrpcEndpoint` -- actually every gRPC leaf imports
`typed_core.grpc.GrpcEndpoint` directly, per `grpc_endpoint()`'s own hardcoded base; this
re-export is for `ChainBase`'s own use and any hand-written caller).

`ChainBase` is the resolved `core` for the whole `chain/` subtree: a heterogeneous
composite (design §5c) of 16 gRPC modules (all sharing one `GrpcClient`) and `comet` (its
own `CometClient`) -- the on-chain gRPC query surface and dYdX Chain's direct CometBFT
JSON-RPC-over-HTTP surface are two distinct transports reachable through one client.
Every one of dYdX's public RPC providers serves both, at matched hostnames, so
`ChainBase`'s own alternate constructors (`.oegs()`, `.polkachu()`, ...) pick one gRPC
host and one Comet URL together -- moved here, consolidated, from what used to be
duplicated across `Dydx`/`Chain`/`Node`'s own hand-written alternate constructors.
"""

from dataclasses import dataclass
from types import TracebackType

from typing_extensions import Self, TypedDict

from typed_core.grpc import GrpcClient, GrpcEndpoint, wrap_exceptions

__all__ = ['GrpcClient', 'GrpcEndpoint', 'wrap_exceptions']
"""Explicit re-export list -- every gRPC leaf, generated and hand-written alike, imports
`GrpcEndpoint`/`wrap_exceptions` from here rather than `typed_core.grpc` directly (the
pre-existing, unmigrated convention this file's own docstring already explains); without
`__all__` pyright treats a bare `from typed_core.grpc import ...` as this module's own
private name and flags every one of those imports (`reportPrivateImportUsage`)."""

from typed_dydx.chain.comet.core import (
  CometClient,
  CometOptions,
  DYDX_COMET_ENIGMA_ARCHIVE_RPC_URL,
  DYDX_COMET_ENIGMA_RPC_URL,
  DYDX_COMET_KINGNODES_ARCHIVE_RPC_URL,
  DYDX_COMET_KINGNODES_RPC_URL,
  DYDX_COMET_OEGS_RPC_URL,
  DYDX_COMET_POLKACHU_ARCHIVE_RPC_URL,
  DYDX_COMET_POLKACHU_RPC_URL,
  DYDX_TESTNET_COMET_KINGNODES_RPC_URL,
  DYDX_TESTNET_COMET_OEGS_RPC_URL,
  DYDX_TESTNET_COMET_POLKACHU_RPC_URL,
)

DYDX_GRPC_OEGS_HOST = 'oegs.dydx.trade'
DYDX_GRPC_POLKACHU_1_HOST = 'dydx-dao-grpc-1.polkachu.com'
DYDX_GRPC_POLKACHU_2_HOST = 'dydx-dao-grpc-2.polkachu.com'
DYDX_GRPC_POLKACHU_3_HOST = 'dydx-dao-grpc-3.polkachu.com'
DYDX_GRPC_KINGNODES_HOST = 'dydx-ops-grpc.kingnodes.com'
DYDX_GRPC_ENIGMA_HOST = 'dydx-dao-grpc.enigma-validator.com'
DYDX_GRPC_POLKACHU_ARCHIVE_1_HOST = 'dydx-dao-archive-grpc-1.polkachu.com'
DYDX_GRPC_KINGNODES_ARCHIVE_HOST = 'dydx-ops-archive-grpc.kingnodes.com'
DYDX_GRPC_ENIGMA_ARCHIVE_HOST = 'dydx-dao-grpc-archive.enigma-validator.com'
DYDX_GRPC_HOSTS = (
  DYDX_GRPC_OEGS_HOST,
  DYDX_GRPC_POLKACHU_1_HOST,
  DYDX_GRPC_POLKACHU_2_HOST,
  DYDX_GRPC_POLKACHU_3_HOST,
  DYDX_GRPC_KINGNODES_HOST,
  DYDX_GRPC_ENIGMA_HOST,
)
DYDX_GRPC_ARCHIVE_HOSTS = (
  DYDX_GRPC_POLKACHU_ARCHIVE_1_HOST,
  DYDX_GRPC_KINGNODES_ARCHIVE_HOST,
  DYDX_GRPC_ENIGMA_ARCHIVE_HOST,
)

DYDX_TESTNET_GRPC_OEGS_HOST = 'oegs-testnet.dydx.exchange'
DYDX_TESTNET_GRPC_KINGNODES_HOST = 'test-dydx-grpc.kingnodes.com'
DYDX_TESTNET_GRPC_POLKACHU_HOST = 'dydx-testnet-grpc.polkachu.com'
DYDX_TESTNET_GRPC_HOSTS = (
  DYDX_TESTNET_GRPC_OEGS_HOST,
  DYDX_TESTNET_GRPC_KINGNODES_HOST,
  DYDX_TESTNET_GRPC_POLKACHU_HOST,
)


class GrpcOptions(TypedDict, total=False):
  """Options for constructing a gRPC transport."""

  port: int
  """gRPC endpoint port."""
  ssl: bool
  """Use TLS for the gRPC channel."""


@dataclass(kw_only=True, frozen=True)
class ChainBase:
  """dYdX Chain client base: one shared `GrpcClient` (16 modules) and one shared
  `CometClient` (`comet`) -- the resolved `core` for `chain/`'s own composite position
  (`codegen/config.toml` `[python.cores.chain]`)."""

  grpc_client: GrpcClient
  comet_client: CometClient

  async def __aenter__(self) -> Self:
    """Open both shared transports for an async context."""
    await self.grpc_client.__aenter__()
    await self.comet_client.__aenter__()
    return self

  async def __aexit__(
    self,
    exc_type: type[BaseException] | None,
    exc: BaseException | None,
    traceback: TracebackType | None,
  ):
    """Close both shared transports for an async context."""
    await self.close()

  async def close(self):
    """Close both shared transports."""
    self.grpc_client.close()
    await self.comet_client.close()

  @classmethod
  def new(cls, client: GrpcClient, *, chain_comet_client: CometClient) -> Self:
    """Build a Chain core forwarding a root client's already-built transports
    (design §5a) -- not meant to be called directly; `client.chain`'s generated
    `@cached_property` calls this, forwarding `DydxBase`'s own `chain_grpc_client`/
    `chain_comet_client` fields.

    Args:
      client: The gRPC transport (`DydxBase.chain_grpc_client`, forwarded as this
        core's own `grpc_client`).
      chain_comet_client: The Comet HTTP transport (`DydxBase.chain_comet_client`).
    """
    return cls(grpc_client=client, comet_client=chain_comet_client)

  @classmethod
  def from_hosts(
    cls, *,
    grpc_host: str = DYDX_GRPC_OEGS_HOST, comet_base_url: str = DYDX_COMET_OEGS_RPC_URL,
    modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a Chain client from raw gRPC host and Comet URL settings.

    Args:
      grpc_host: gRPC endpoint host.
      comet_base_url: Comet HTTP base URL.
      modules: Optional gRPC transport overrides (port/ssl).
      comet: Optional Comet HTTP transport overrides (http/validate).
    """
    return cls(
      grpc_client=GrpcClient(host=grpc_host, **(modules or {})),
      comet_client=CometClient(base_url=comet_base_url, **(comet or {})),
    )

  @classmethod
  def oegs(cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None) -> Self:
    """Create a Chain client for the OEGS mainnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_GRPC_OEGS_HOST, comet_base_url=DYDX_COMET_OEGS_RPC_URL,
      modules=modules, comet=comet,
    )

  @classmethod
  def polkachu(cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None) -> Self:
    """Create a Chain client for the Polkachu mainnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_GRPC_POLKACHU_1_HOST, comet_base_url=DYDX_COMET_POLKACHU_RPC_URL,
      modules=modules, comet=comet,
    )

  @classmethod
  def kingnodes(cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None) -> Self:
    """Create a Chain client for the KingNodes mainnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_GRPC_KINGNODES_HOST, comet_base_url=DYDX_COMET_KINGNODES_RPC_URL,
      modules=modules, comet=comet,
    )

  @classmethod
  def enigma(cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None) -> Self:
    """Create a Chain client for the Enigma mainnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_GRPC_ENIGMA_HOST, comet_base_url=DYDX_COMET_ENIGMA_RPC_URL,
      modules=modules, comet=comet,
    )

  @classmethod
  def polkachu_archive(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a Chain client for the Polkachu archive mainnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_GRPC_POLKACHU_ARCHIVE_1_HOST,
      comet_base_url=DYDX_COMET_POLKACHU_ARCHIVE_RPC_URL,
      modules=modules, comet=comet,
    )

  @classmethod
  def kingnodes_archive(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a Chain client for the KingNodes archive mainnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_GRPC_KINGNODES_ARCHIVE_HOST,
      comet_base_url=DYDX_COMET_KINGNODES_ARCHIVE_RPC_URL,
      modules=modules, comet=comet,
    )

  @classmethod
  def enigma_archive(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a Chain client for the Enigma archive mainnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_GRPC_ENIGMA_ARCHIVE_HOST,
      comet_base_url=DYDX_COMET_ENIGMA_ARCHIVE_RPC_URL,
      modules=modules, comet=comet,
    )

  @classmethod
  def testnet_oegs(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a Chain client for the OEGS testnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_TESTNET_GRPC_OEGS_HOST, comet_base_url=DYDX_TESTNET_COMET_OEGS_RPC_URL,
      modules=modules, comet=comet,
    )

  @classmethod
  def testnet_kingnodes(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a Chain client for the KingNodes testnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_TESTNET_GRPC_KINGNODES_HOST,
      comet_base_url=DYDX_TESTNET_COMET_KINGNODES_RPC_URL,
      modules=modules, comet=comet,
    )

  @classmethod
  def testnet_polkachu(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a Chain client for the Polkachu testnet provider."""
    return cls.from_hosts(
      grpc_host=DYDX_TESTNET_GRPC_POLKACHU_HOST,
      comet_base_url=DYDX_TESTNET_COMET_POLKACHU_RPC_URL,
      modules=modules, comet=comet,
    )
