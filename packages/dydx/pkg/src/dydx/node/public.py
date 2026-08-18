"""Public dYdX node query helpers."""

from dataclasses import dataclass

from dydx.chain import Chain
from dydx.protos.cosmos.auth import v1beta1 as auth_proto
from dydx.protos.cosmos.bank import v1beta1 as bank_proto
from dydx.protos.cosmos.base.tendermint import v1beta1 as tendermint_proto
from dydx.protos.cosmos.tx import v1beta1 as tx_proto
from dydx.protos.dydxprotocol import clob as clob_proto
from dydx.protos.dydxprotocol import prices as prices_proto
from dydx.protos.dydxprotocol import subaccounts as subaccounts_proto

@dataclass
class Public:
  """Read-only node queries that proxy chain modules."""

  chain: Chain
  """Chain client used for read-only gRPC queries."""

  async def get_account(self, address: str) -> auth_proto.QueryAccountResponse:
    """Query a chain account.

    Args:
      address: dYdX bech32 account address.

    Returns:
      Cosmos auth account query response.
    """
    return await self.chain.auth.account(address)

  async def get_account_balances(self, address: str) -> bank_proto.QueryAllBalancesResponse:
    """Query all balances for an account.

    Args:
      address: dYdX bech32 account address.

    Returns:
      Cosmos bank all-balances query response.
    """
    return await self.chain.bank.all_balances(address, resolve_denom=False)

  async def get_balance(self, *, address: str, denom: str) -> bank_proto.QueryBalanceResponse:
    """Query one balance for an account.

    Args:
      address: dYdX bech32 account address.
      denom: Cosmos denomination to query.

    Returns:
      Cosmos bank balance query response.
    """
    return await self.chain.bank.balance(address=address, denom=denom)

  async def get_latest_block(self) -> tendermint_proto.GetLatestBlockResponse:
    """Query the latest block.

    Returns:
      Latest block response from the Cosmos Tendermint service.
    """
    return await self.chain.tendermint.get_latest_block()

  async def get_block_by_height(self, height: int) -> tendermint_proto.GetBlockByHeightResponse:
    """Query a block by height.

    Args:
      height: Block height to query.

    Returns:
      Block response from the Cosmos Tendermint service.
    """
    return await self.chain.tendermint.get_block_by_height(height)

  async def get_tx(self, hash: str) -> tx_proto.GetTxResponse:
    """Query a transaction by hash.

    Args:
      hash: Transaction hash in hex form.

    Returns:
      Cosmos transaction query response.
    """
    return await self.chain.tx.get_tx(hash)

  async def get_clob_pair(self, id: int) -> clob_proto.QueryClobPairResponse:
    """Query a CLOB pair.

    Args:
      id: dYdX CLOB pair ID.

    Returns:
      CLOB pair query response.
    """
    return await self.chain.clob.clob_pair(id)

  async def get_clob_pairs(self) -> clob_proto.QueryClobPairAllResponse:
    """Query CLOB pairs.

    Returns:
      CLOB pair list query response.
    """
    return await self.chain.clob.clob_pairs()

  async def get_price(self, id: int) -> prices_proto.QueryMarketPriceResponse:
    """Query a market price.

    Args:
      id: dYdX market ID.

    Returns:
      Market price query response.
    """
    return await self.chain.prices.market_price(id)

  async def get_subaccount(
    self, *, owner: str, number: int = 0,
  ) -> subaccounts_proto.QuerySubaccountResponse:
    """Query a subaccount.

    Args:
      owner: dYdX bech32 owner address.
      number: dYdX subaccount number under the owner address.

    Returns:
      Subaccount query response.
    """
    return await self.chain.subaccounts.subaccount(owner, number=number)

  async def simulate_tx_bytes(self, tx_bytes: bytes) -> tx_proto.SimulateResponse:
    """Simulate raw transaction bytes.

    Args:
      tx_bytes: Encoded `TxRaw` bytes.

    Returns:
      Cosmos transaction simulation response.
    """
    return await self.chain.tx.simulate(tx_bytes=tx_bytes)

  async def broadcast_tx_bytes(
    self,
    tx_bytes: bytes,
    *,
    mode: tx_proto.BroadcastMode = tx_proto.BroadcastMode(2),
  ) -> tx_proto.BroadcastTxResponse:
    """Broadcast raw transaction bytes.

    Args:
      tx_bytes: Encoded `TxRaw` bytes.
      mode: Cosmos broadcast mode.

    Returns:
      Cosmos transaction broadcast response.
    """
    return await self.chain.tx.broadcast(tx_bytes, mode=mode)
