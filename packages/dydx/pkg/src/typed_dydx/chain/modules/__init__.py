"""dYdX Chain module groups."""

from dataclasses import dataclass
from functools import cached_property
from types import TracebackType

from typing_extensions import Self, TypedDict, Unpack

from typed_dydx.chain.core import GrpcClient
from typed_dydx.chain.modules.affiliates import Affiliates
from typed_dydx.chain.modules.assets import Assets
from typed_dydx.chain.modules.auth import Auth
from typed_dydx.chain.modules.bank import Bank
from typed_dydx.chain.modules.clob import Clob
from typed_dydx.chain.modules.distribution import Distribution
from typed_dydx.chain.modules.feetiers import Feetiers
from typed_dydx.chain.modules.gov import Gov
from typed_dydx.chain.modules.perpetuals import Perpetuals
from typed_dydx.chain.modules.prices import Prices
from typed_dydx.chain.modules.revshare import Revshare
from typed_dydx.chain.modules.rewards import Rewards
from typed_dydx.chain.modules.staking import Staking
from typed_dydx.chain.modules.subaccounts import Subaccounts
from typed_dydx.chain.modules.tendermint import Tendermint
from typed_dydx.chain.modules.tx import Tx

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

class ModulesOptions(TypedDict, total=False):
  """Options shared by gRPC module constructors."""

  client: GrpcClient
  """Existing gRPC transport shared by module adapters."""

class GrpcOptions(TypedDict, total=False):
  """Options for constructing a gRPC transport."""

  port: int
  """gRPC endpoint port."""
  ssl: bool
  """Use TLS for the gRPC channel."""

@dataclass(kw_only=True, frozen=True)
class Modules:
  """Composed dYdX Chain module groups."""

  client: GrpcClient

  @cached_property
  def auth(self) -> Auth:
    return Auth(client=self.client)

  @cached_property
  def bank(self) -> Bank:
    return Bank(client=self.client)

  @cached_property
  def tx(self) -> Tx:
    return Tx(client=self.client)

  @cached_property
  def tendermint(self) -> Tendermint:
    return Tendermint(client=self.client)

  @cached_property
  def staking(self) -> Staking:
    return Staking(client=self.client)

  @cached_property
  def distribution(self) -> Distribution:
    return Distribution(client=self.client)

  @cached_property
  def subaccounts(self) -> Subaccounts:
    return Subaccounts(client=self.client)

  @cached_property
  def clob(self) -> Clob:
    return Clob(client=self.client)

  @cached_property
  def prices(self) -> Prices:
    return Prices(client=self.client)

  @cached_property
  def perpetuals(self) -> Perpetuals:
    return Perpetuals(client=self.client)

  @cached_property
  def assets(self) -> Assets:
    return Assets(client=self.client)

  @cached_property
  def feetiers(self) -> Feetiers:
    return Feetiers(client=self.client)

  @cached_property
  def rewards(self) -> Rewards:
    return Rewards(client=self.client)

  @cached_property
  def affiliates(self) -> Affiliates:
    return Affiliates(client=self.client)

  @cached_property
  def revshare(self) -> Revshare:
    return Revshare(client=self.client)

  @cached_property
  def gov(self) -> Gov:
    return Gov(client=self.client)

  async def __aenter__(self) -> Self:
    """Open the shared gRPC transport for an async context."""
    await self.client.__aenter__()
    return self

  async def __aexit__(
    self,
    exc_type: type[BaseException] | None,
    exc: BaseException | None,
    traceback: TracebackType | None,
  ):
    """Close the shared gRPC transport for an async context."""
    await self.client.__aexit__(exc_type, exc, traceback)

  @classmethod
  def new(cls, host: str, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for a custom gRPC endpoint."""
    return cls(client=GrpcClient(host=host, **kwargs))

  @classmethod
  def from_client(cls, client: GrpcClient) -> Self:
    """Create module groups from an existing gRPC transport."""
    return cls(client=client)

  @classmethod
  def oegs(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the OEGS mainnet gRPC endpoint."""
    return cls.new(DYDX_GRPC_OEGS_HOST, **kwargs)

  @classmethod
  def polkachu(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the first Polkachu mainnet gRPC endpoint."""
    return cls.new(DYDX_GRPC_POLKACHU_1_HOST, **kwargs)

  @classmethod
  def polkachu_2(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the second Polkachu mainnet gRPC endpoint."""
    return cls.new(DYDX_GRPC_POLKACHU_2_HOST, **kwargs)

  @classmethod
  def polkachu_3(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the third Polkachu mainnet gRPC endpoint."""
    return cls.new(DYDX_GRPC_POLKACHU_3_HOST, **kwargs)

  @classmethod
  def kingnodes(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the KingNodes mainnet gRPC endpoint."""
    return cls.new(DYDX_GRPC_KINGNODES_HOST, **kwargs)

  @classmethod
  def enigma(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the Enigma mainnet gRPC endpoint."""
    return cls.new(DYDX_GRPC_ENIGMA_HOST, **kwargs)

  @classmethod
  def polkachu_archive(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the Polkachu archive mainnet gRPC endpoint."""
    return cls.new(DYDX_GRPC_POLKACHU_ARCHIVE_1_HOST, **kwargs)

  @classmethod
  def kingnodes_archive(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the KingNodes archive mainnet gRPC endpoint."""
    return cls.new(DYDX_GRPC_KINGNODES_ARCHIVE_HOST, **kwargs)

  @classmethod
  def enigma_archive(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the Enigma archive mainnet gRPC endpoint."""
    return cls.new(DYDX_GRPC_ENIGMA_ARCHIVE_HOST, **kwargs)

  @classmethod
  def testnet_oegs(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the OEGS testnet gRPC endpoint."""
    return cls.new(DYDX_TESTNET_GRPC_OEGS_HOST, **kwargs)

  @classmethod
  def testnet_kingnodes(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the KingNodes testnet gRPC endpoint."""
    return cls.new(DYDX_TESTNET_GRPC_KINGNODES_HOST, **kwargs)

  @classmethod
  def testnet_polkachu(cls, **kwargs: Unpack[GrpcOptions]) -> Self:
    """Create module groups for the Polkachu plaintext testnet gRPC endpoint."""
    port = kwargs.get('port', 23890)
    ssl = kwargs.get('ssl', False)
    return cls.new(DYDX_TESTNET_GRPC_POLKACHU_HOST, port=port, ssl=ssl)
