"""dYdX Chain Comet HTTP endpoints."""

from typed_dydx.chain.comet.block import Block
from typed_dydx.chain.comet.block_results import BlockResults
from typed_dydx.chain.comet.core import (
  CometOptions,
  CometEndpoint,
  CometRouter,
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
)
from typed_dydx.chain.comet.status import Status
from typed_dydx.chain.comet.tx import Tx
from typed_dydx.chain.comet.tx_search import TxSearch
from typing_extensions import Self, Unpack


class Comet(
  Status,
  Block,
  BlockResults,
  Tx,
  TxSearch,
  CometRouter,
):
  """Read-only dYdX Chain Comet HTTP endpoint group."""

  @classmethod
  def new(cls, base_url: str, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for a custom RPC endpoint."""
    return cls(base_url=base_url, **kwargs)

  @classmethod
  def oegs(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the OEGS mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_OEGS_RPC_URL, **kwargs)

  @classmethod
  def polkachu(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the Polkachu mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_POLKACHU_RPC_URL, **kwargs)

  @classmethod
  def kingnodes(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the KingNodes mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_KINGNODES_RPC_URL, **kwargs)

  @classmethod
  def enigma(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the Enigma mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_ENIGMA_RPC_URL, **kwargs)

  @classmethod
  def polkachu_archive(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the Polkachu archive mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_POLKACHU_ARCHIVE_RPC_URL, **kwargs)

  @classmethod
  def kingnodes_archive(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the KingNodes archive mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_KINGNODES_ARCHIVE_RPC_URL, **kwargs)

  @classmethod
  def enigma_archive(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the Enigma archive mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_ENIGMA_ARCHIVE_RPC_URL, **kwargs)

  @classmethod
  def publicnode(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the PublicNode community mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_PUBLICNODE_RPC_URL, **kwargs)

  @classmethod
  def lavenderfive(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the Lavender.Five community mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_LAVENDERFIVE_RPC_URL, **kwargs)

  @classmethod
  def imperator(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the Imperator community mainnet RPC endpoint."""
    return cls.new(DYDX_COMET_IMPERATOR_RPC_URL, **kwargs)

  @classmethod
  def testnet_oegs(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the OEGS testnet RPC endpoint."""
    return cls.new(DYDX_TESTNET_COMET_OEGS_RPC_URL, **kwargs)

  @classmethod
  def testnet_enigma(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the Enigma testnet RPC endpoint."""
    return cls.new(DYDX_TESTNET_COMET_ENIGMA_RPC_URL, **kwargs)

  @classmethod
  def testnet_kingnodes(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the KingNodes testnet RPC endpoint."""
    return cls.new(DYDX_TESTNET_COMET_KINGNODES_RPC_URL, **kwargs)

  @classmethod
  def testnet_polkachu(cls, **kwargs: Unpack[CometOptions]) -> Self:
    """Create a Comet client for the Polkachu testnet RPC endpoint."""
    return cls.new(DYDX_TESTNET_COMET_POLKACHU_RPC_URL, **kwargs)
