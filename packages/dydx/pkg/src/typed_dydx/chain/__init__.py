"""dYdX Chain client."""

from dataclasses import dataclass, field
from types import TracebackType

from typed_core.http import HttpClient
from typing_extensions import Self

from typed_dydx.chain.comet import Comet
from typed_dydx.chain.comet.core import (
  DYDX_COMET_ARCHIVE_RPC_URLS,
  DYDX_COMET_COMMUNITY_RPC_URLS,
  DYDX_COMET_ENIGMA_ARCHIVE_RPC_URL,
  DYDX_COMET_ENIGMA_RPC_URL,
  DYDX_COMET_IMPERATOR_RPC_URL,
  DYDX_COMET_KINGNODES_ARCHIVE_RPC_URL,
  DYDX_COMET_KINGNODES_RPC_URL,
  DYDX_COMET_LAVENDERFIVE_RPC_URL,
  DYDX_COMET_OEGS_RPC_URL,
  DYDX_COMET_POLKACHU_ARCHIVE_RPC_URL,
  DYDX_COMET_POLKACHU_RPC_URL,
  DYDX_COMET_PUBLICNODE_RPC_URL,
  DYDX_COMET_RPC_URL,
  DYDX_COMET_RPC_URLS,
  DYDX_TESTNET_COMET_ENIGMA_RPC_URL,
  DYDX_TESTNET_COMET_KINGNODES_RPC_URL,
  DYDX_TESTNET_COMET_OEGS_RPC_URL,
  DYDX_TESTNET_COMET_POLKACHU_RPC_URL,
  DYDX_TESTNET_COMET_RPC_URL,
  DYDX_TESTNET_COMET_RPC_URLS,
  CometOptions,
)
from typed_dydx.chain.modules import (
  DYDX_GRPC_ENIGMA_HOST,
  DYDX_GRPC_KINGNODES_HOST,
  DYDX_GRPC_OEGS_HOST,
  DYDX_GRPC_POLKACHU_1_HOST,
  DYDX_GRPC_POLKACHU_ARCHIVE_1_HOST,
  DYDX_GRPC_KINGNODES_ARCHIVE_HOST,
  DYDX_GRPC_ENIGMA_ARCHIVE_HOST,
  DYDX_TESTNET_GRPC_KINGNODES_HOST,
  DYDX_TESTNET_GRPC_OEGS_HOST,
  GrpcOptions,
  Modules,
)
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

@dataclass
class Chain:
  """Composed dYdX Chain client."""

  modules: Modules = field(default_factory=Modules.oegs)
  comet: Comet = field(default_factory=Comet.oegs)

  @classmethod
  def new(
    cls,
    *,
    grpc_host: str = DYDX_GRPC_OEGS_HOST,
    grpc_port: int = 443,
    grpc_ssl: bool = True,
    comet_base_url: str = DYDX_COMET_OEGS_RPC_URL,
    http: HttpClient | None = None,
    validate: bool = True,
  ) -> Self:
    """Create a chain client from raw gRPC and Comet endpoint settings."""
    comet = Comet(base_url=comet_base_url, validate=validate)
    if http is not None:
      comet.http = http
    return cls(
      modules=Modules.new(grpc_host, port=grpc_port, ssl=grpc_ssl),
      comet=comet,
    )

  @classmethod
  def oegs(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for OEGS mainnet endpoints."""
    return cls(modules=Modules.oegs(**(modules or {})), comet=Comet.oegs(**(comet or {})))

  @classmethod
  def polkachu(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for Polkachu mainnet endpoints."""
    return cls(modules=Modules.polkachu(**(modules or {})), comet=Comet.polkachu(**(comet or {})))

  @classmethod
  def kingnodes(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for KingNodes mainnet endpoints."""
    return cls(modules=Modules.kingnodes(**(modules or {})), comet=Comet.kingnodes(**(comet or {})))

  @classmethod
  def enigma(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for Enigma mainnet endpoints."""
    return cls(modules=Modules.enigma(**(modules or {})), comet=Comet.enigma(**(comet or {})))

  @classmethod
  def polkachu_archive(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for Polkachu archive mainnet endpoints."""
    return cls(
      modules=Modules.polkachu_archive(**(modules or {})),
      comet=Comet.polkachu_archive(**(comet or {})),
    )

  @classmethod
  def kingnodes_archive(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for KingNodes archive mainnet endpoints."""
    return cls(
      modules=Modules.kingnodes_archive(**(modules or {})),
      comet=Comet.kingnodes_archive(**(comet or {})),
    )

  @classmethod
  def enigma_archive(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for Enigma archive mainnet endpoints."""
    return cls(
      modules=Modules.enigma_archive(**(modules or {})),
      comet=Comet.enigma_archive(**(comet or {})),
    )

  @classmethod
  def testnet_oegs(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for OEGS testnet endpoints."""
    return cls(
      modules=Modules.testnet_oegs(**(modules or {})),
      comet=Comet.testnet_oegs(**(comet or {})),
    )

  @classmethod
  def testnet_kingnodes(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for KingNodes testnet endpoints."""
    return cls(
      modules=Modules.testnet_kingnodes(**(modules or {})),
      comet=Comet.testnet_kingnodes(**(comet or {})),
    )

  @classmethod
  def testnet_polkachu(
    cls, *, modules: GrpcOptions | None = None, comet: CometOptions | None = None,
  ) -> Self:
    """Create a chain client for Polkachu testnet endpoints."""
    return cls(
      modules=Modules.testnet_polkachu(**(modules or {})),
      comet=Comet.testnet_polkachu(**(comet or {})),
    )

  @property
  def auth(self) -> Auth:
    """Return auth module queries."""
    return self.modules.auth

  @property
  def bank(self) -> Bank:
    """Return bank module queries."""
    return self.modules.bank

  @property
  def tx(self) -> Tx:
    """Return tx module queries."""
    return self.modules.tx

  @property
  def tendermint(self) -> Tendermint:
    """Return Tendermint service queries."""
    return self.modules.tendermint

  @property
  def staking(self) -> Staking:
    """Return staking module queries."""
    return self.modules.staking

  @property
  def distribution(self) -> Distribution:
    """Return distribution module queries."""
    return self.modules.distribution

  @property
  def subaccounts(self) -> Subaccounts:
    """Return dYdX subaccount queries."""
    return self.modules.subaccounts

  @property
  def clob(self) -> Clob:
    """Return dYdX CLOB queries."""
    return self.modules.clob

  @property
  def prices(self) -> Prices:
    """Return dYdX price queries."""
    return self.modules.prices

  @property
  def perpetuals(self) -> Perpetuals:
    """Return dYdX perpetual queries."""
    return self.modules.perpetuals

  @property
  def assets(self) -> Assets:
    """Return dYdX asset queries."""
    return self.modules.assets

  @property
  def feetiers(self) -> Feetiers:
    """Return dYdX fee-tier queries."""
    return self.modules.feetiers

  @property
  def rewards(self) -> Rewards:
    """Return dYdX reward queries."""
    return self.modules.rewards

  @property
  def affiliates(self) -> Affiliates:
    """Return dYdX affiliate queries."""
    return self.modules.affiliates

  @property
  def revshare(self) -> Revshare:
    """Return dYdX revenue-share queries."""
    return self.modules.revshare

  @property
  def gov(self) -> Gov:
    """Return dYdX governance queries."""
    return self.modules.gov

  async def __aenter__(self) -> Self:
    """Enter the chain client context."""
    await self.modules.__aenter__()
    await self.comet.__aenter__()
    return self

  async def __aexit__(
    self,
    exc_type: type[BaseException] | None,
    exc: BaseException | None,
    traceback: TracebackType | None,
  ):
    """Close chain transports when leaving a context."""
    await self.close()

  async def close(self):
    """Close gRPC and Comet transports."""
    await self.modules.__aexit__(None, None, None)
    await self.comet.__aexit__(None, None, None)
