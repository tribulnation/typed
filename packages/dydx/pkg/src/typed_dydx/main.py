"""Top-level dYdX client composition."""

import asyncio
from dataclasses import dataclass
from types import TracebackType

from typing_extensions import Self

from typed_dydx.chain import Chain
from typed_dydx.chain.comet.core import CometOptions
from typed_dydx.chain.modules import GrpcOptions
from typed_dydx.indexer import Indexer, IndexerOptions
from typed_dydx.node.constants import (
  DYDX_MAINNET_CHAIN_ID,
  DYDX_MAINNET_USDC_DENOM,
  DYDX_TESTNET_CHAIN_ID,
  DYDX_TESTNET_USDC_DENOM,
)
from typed_dydx.node.core import Node

@dataclass
class Dydx:
  """Composed dYdX client for indexer, chain, and node workflows."""

  indexer: Indexer
  """Indexer HTTP and WebSocket client for market data and account history."""
  chain: Chain
  """Shared chain client for gRPC queries and Comet lookups."""
  node: Node
  """Node helper surface for signing, broadcasting, and trading."""

  @classmethod
  def new(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: Indexer | None = None,
    chain: Chain | None = None,
    public: bool = False,
    chain_id: str = DYDX_MAINNET_CHAIN_ID,
    usdc_denom: str = DYDX_MAINNET_USDC_DENOM,
    memo: str = '',
    mnemonic_env: str = 'DYDX_MNEMONIC',
  ) -> Self:
    """Create a top-level client from existing indexer and chain clients.

    Args:
      mnemonic: Optional wallet mnemonic. When omitted, `mnemonic_env` is read.
      indexer: Indexer HTTP and WebSocket client.
      chain: Chain client shared by `chain` and `node`.
      public: Allow construction without a wallet for read-only workflows.
      chain_id: Cosmos chain ID included in transaction sign docs.
      usdc_denom: USDC denomination used when building transaction fees.
      memo: Default transaction memo used when signing.
      mnemonic_env: Environment variable consulted when `mnemonic` is omitted.

    Returns:
      A composed dYdX client with shared chain transport.
    """
    indexer = indexer or Indexer()
    chain = chain or Chain()
    return cls(
      indexer=indexer,
      chain=chain,
      node=Node.new(
        chain=chain,
        chain_id=chain_id,
        usdc_denom=usdc_denom,
        mnemonic=mnemonic,
        public=public,
        mnemonic_env=mnemonic_env,
        memo=memo,
      ),
    )

  @classmethod
  def oegs(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a mainnet dYdX client for OEGS chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed mainnet client backed by OEGS chain endpoints.
    """
    chain = Chain.oegs(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.new(**(indexer or {})),
      chain=chain,
      public=public,
      memo=memo,
    )

  @classmethod
  def mainnet(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create the default mainnet dYdX client.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed mainnet client using the default provider.
    """
    return cls.oegs(
      mnemonic,
      indexer=indexer,
      modules=modules,
      comet=comet,
      public=public,
      memo=memo,
    )

  @classmethod
  def polkachu(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a mainnet dYdX client for Polkachu chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed mainnet client backed by Polkachu chain endpoints.
    """
    chain = Chain.polkachu(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.new(**(indexer or {})),
      chain=chain,
      public=public,
      memo=memo,
    )

  @classmethod
  def kingnodes(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a mainnet dYdX client for KingNodes chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed mainnet client backed by KingNodes chain endpoints.
    """
    chain = Chain.kingnodes(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.new(**(indexer or {})),
      chain=chain,
      public=public,
      memo=memo,
    )

  @classmethod
  def enigma(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a mainnet dYdX client for Enigma chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed mainnet client backed by Enigma chain endpoints.
    """
    chain = Chain.enigma(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.new(**(indexer or {})),
      chain=chain,
      public=public,
      memo=memo,
    )

  @classmethod
  def polkachu_archive(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a mainnet dYdX client for Polkachu archive chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed mainnet client backed by Polkachu archive endpoints.
    """
    chain = Chain.polkachu_archive(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.new(**(indexer or {})),
      chain=chain,
      public=public,
      memo=memo,
    )

  @classmethod
  def kingnodes_archive(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a mainnet dYdX client for KingNodes archive chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed mainnet client backed by KingNodes archive endpoints.
    """
    chain = Chain.kingnodes_archive(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.new(**(indexer or {})),
      chain=chain,
      public=public,
      memo=memo,
    )

  @classmethod
  def enigma_archive(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a mainnet dYdX client for Enigma archive chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed mainnet client backed by Enigma archive endpoints.
    """
    chain = Chain.enigma_archive(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.new(**(indexer or {})),
      chain=chain,
      public=public,
      memo=memo,
    )

  @classmethod
  def testnet_oegs(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a testnet dYdX client for OEGS chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_TESTNET_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed testnet client backed by OEGS chain endpoints.
    """
    chain = Chain.testnet_oegs(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.testnet(**(indexer or {})),
      chain=chain,
      public=public,
      chain_id=DYDX_TESTNET_CHAIN_ID,
      usdc_denom=DYDX_TESTNET_USDC_DENOM,
      memo=memo,
      mnemonic_env='DYDX_TESTNET_MNEMONIC',
    )

  @classmethod
  def testnet(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create the default testnet dYdX client.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_TESTNET_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed testnet client using the default provider.
    """
    return cls.testnet_kingnodes(
      mnemonic,
      indexer=indexer,
      modules=modules,
      comet=comet,
      public=public,
      memo=memo,
    )

  @classmethod
  def testnet_kingnodes(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a testnet dYdX client for KingNodes chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_TESTNET_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed testnet client backed by KingNodes chain endpoints.
    """
    chain = Chain.testnet_kingnodes(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.testnet(**(indexer or {})),
      chain=chain,
      public=public,
      chain_id=DYDX_TESTNET_CHAIN_ID,
      usdc_denom=DYDX_TESTNET_USDC_DENOM,
      memo=memo,
      mnemonic_env='DYDX_TESTNET_MNEMONIC',
    )

  @classmethod
  def testnet_polkachu(
    cls,
    mnemonic: str | None = None,
    *,
    indexer: IndexerOptions | None = None,
    modules: GrpcOptions | None = None,
    comet: CometOptions | None = None,
    public: bool = False,
    memo: str = '',
  ) -> Self:
    """Create a testnet dYdX client for Polkachu chain endpoints.

    Args:
      mnemonic: Optional wallet mnemonic. Falls back to `DYDX_TESTNET_MNEMONIC`.
      indexer: Optional indexer transport overrides.
      modules: Optional gRPC transport overrides.
      comet: Optional Comet HTTP transport overrides.
      public: Allow read-only construction without a mnemonic.
      memo: Default transaction memo used when signing.

    Returns:
      A composed testnet client backed by Polkachu chain endpoints.
    """
    chain = Chain.testnet_polkachu(modules=modules, comet=comet)
    return cls.new(
      mnemonic,
      indexer=Indexer.testnet(**(indexer or {})),
      chain=chain,
      public=public,
      chain_id=DYDX_TESTNET_CHAIN_ID,
      usdc_denom=DYDX_TESTNET_USDC_DENOM,
      memo=memo,
      mnemonic_env='DYDX_TESTNET_MNEMONIC',
    )

  async def __aenter__(self) -> Self:
    """Enter indexer and chain transports."""
    await self.indexer.__aenter__()
    await self.chain.__aenter__()
    if self.node.wallet is not None:
      await self.node.refresh_wallet()
    return self

  async def __aexit__(
    self,
    exc_type: type[BaseException] | None,
    exc: BaseException | None,
    traceback: TracebackType | None,
  ):
    """Close indexer and chain transports."""
    await self.close()

  async def close(self):
    """Close all top-level transports."""
    await asyncio.gather(
      self.indexer.__aexit__(None, None, None),
      self.chain.close(),
    )
