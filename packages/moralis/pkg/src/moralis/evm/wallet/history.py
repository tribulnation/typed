"""Moralis EVM decoded wallet history endpoint."""
from typing_extensions import Literal, NotRequired, Required, TypedDict
from pydantic import TypeAdapter

from typed_core import PaginatedResponse
from moralis.core import Chain, Direction, Endpoint, Order, clean_params
from .token_transfers import TokenTransfer


class NativeTransfer(TypedDict, total=False):
  """Native asset transfer decoded from a wallet transaction."""
  from_address: Required[str]
  """Sender address."""
  from_address_label: str | None
  """Sender address label."""
  to_address: Required[str]
  """Recipient address."""
  to_address_label: str | None
  """Recipient address label."""
  value: Required[str]
  """Raw integer native amount."""
  value_formatted: str | None
  """Human-readable native amount."""
  direction: NotRequired[Direction]
  """Wallet-relative transfer direction, when provided."""
  internal_transaction: bool
  """Whether this transfer came from an internal transaction."""
  token_symbol: str | None
  """Native asset symbol."""
  token_logo: str | None
  """Native asset logo URL."""


class NftTransfer(TypedDict, total=False):
  """NFT transfer decoded from a wallet transaction."""
  token_address: Required[str]
  """NFT contract address."""
  token_id: str | None
  """NFT token ID."""
  from_address: str | None
  """Sender address."""
  to_address: str | None
  """Recipient address."""
  amount: str | None
  """NFT amount."""
  contract_type: str | None
  """NFT contract standard."""
  token_uri: str | None
  """NFT metadata URI."""
  verified_collection: bool
  """Whether Moralis marks the collection as verified."""
  possible_spam: bool
  """Whether Moralis marks the NFT as possible spam."""


class WalletHistoryTransaction(TypedDict, total=False):
  """Decoded transaction in a wallet history page."""
  hash: Required[str]
  """Transaction hash."""
  nonce: str
  """Transaction nonce."""
  transaction_index: str | int
  """Transaction index in the block."""
  from_address: Required[str]
  """Transaction sender address."""
  to_address: str | None
  """Transaction recipient address."""
  value: str
  """Raw integer native value."""
  gas: str
  """Gas limit."""
  gas_price: str
  """Gas price."""
  receipt_cumulative_gas_used: str
  """Cumulative gas used at transaction execution."""
  receipt_gas_used: str
  """Gas used by the transaction."""
  receipt_contract_address: str | None
  """Created contract address, when applicable."""
  receipt_status: str | None
  """Transaction receipt status."""
  block_timestamp: str
  """Block timestamp in upstream format."""
  block_number: str
  """Block number."""
  block_hash: str
  """Block hash."""
  transaction_fee: str | None
  """Native transaction fee paid by the sender."""
  method_label: str | None
  """Decoded method label."""
  from_address_label: str | None
  """Sender address label."""
  from_address_entity: str | None
  """Sender entity label."""
  from_address_entity_logo: str | None
  """Sender entity logo URL."""
  to_address_label: str | None
  """Recipient address label."""
  to_address_entity: str | None
  """Recipient entity label."""
  to_address_entity_logo: str | None
  """Recipient entity logo URL."""
  nft_transfers: list[NftTransfer]
  """NFT transfers decoded from the transaction."""
  erc20_transfers: list[TokenTransfer]
  """ERC20 transfers decoded from the transaction."""
  native_transfers: list[NativeTransfer]
  """Native transfers decoded from the transaction."""
  summary: str | None
  """Moralis transaction summary."""
  possible_spam: bool
  """Whether Moralis marks the transaction as possible spam."""
  category: str | None
  """Moralis transaction category."""
  input: str | None


class WalletHistoryResponse(TypedDict, total=False):
  """Moralis decoded wallet history page."""
  synced_at: int
  """Latest synced block at response time."""
  page_size: int
  """Number of transactions returned."""
  page: int
  """Page number."""
  limit: int
  """Requested page limit."""
  result: Required[list[WalletHistoryTransaction]]
  """Decoded wallet transactions in this page."""
  cursor: str | None
  """Cursor for the next page."""


HistoryCategory = Literal[
  'contract interaction',
  'external',
  'internal',
  'mint',
  'nft receive',
  'nft send',
  'receive',
  'send',
  'swap',
  'token receive',
  'token send',
]
"""Known Moralis wallet-history category filter."""

history_adapter = TypeAdapter(WalletHistoryResponse)


class History(Endpoint):
  """Moralis EVM decoded wallet history endpoints."""

  async def history(
    self, address: str, /, *,
    chain: Chain,
    from_date: str | None = None,
    to_date: str | None = None,
    from_block: int | None = None,
    to_block: int | None = None,
    cursor: str | None = None,
    limit: int | None = None,
    order: Order | None = None,
    include_internal_transactions: bool | None = None,
    nft_metadata: bool | None = None,
    category: HistoryCategory | None = None,
    validate: bool | None = None,
  ) -> WalletHistoryResponse:
    """Fetch decoded transaction history for a wallet.

    Args:
      address: Wallet address.
      chain: Moralis EVM chain identifier.
      from_date: Inclusive lower timestamp bound accepted by Moralis.
      to_date: Inclusive upper timestamp bound accepted by Moralis.
      from_block: Inclusive lower block bound.
      to_block: Inclusive upper block bound.
      cursor: Moralis pagination cursor.
      limit: Maximum page size.
      order: Sort order.
      include_internal_transactions: Include decoded internal transactions.
      nft_metadata: Include NFT metadata.
      category: Moralis transaction category filter.
      validate: Per-call response validation override.

    Returns:
      A page of decoded wallet transactions.

    References:
      Upstream docs: https://docs.moralis.com/web3-data-api/evm/reference/wallet-api/get-wallet-history
    """
    params = clean_params({
      'chain': chain,
      'from_date': from_date,
      'to_date': to_date,
      'from_block': from_block,
      'to_block': to_block,
      'cursor': cursor,
      'limit': limit,
      'order': order,
      'include_internal_transactions': include_internal_transactions,
      'nft_metadata': nft_metadata,
      'category': category,
    })
    response = await self.request('GET', f'/wallets/{address}/history', params=params)
    if self.should_validate(validate):
      return history_adapter.validate_json(response.text)
    return response.json()

  def history_paged(
    self, address: str, /, *,
    chain: Chain,
    from_date: str | None = None,
    to_date: str | None = None,
    from_block: int | None = None,
    to_block: int | None = None,
    cursor: str | None = None,
    limit: int | None = None,
    order: Order | None = None,
    include_internal_transactions: bool | None = None,
    nft_metadata: bool | None = None,
    category: HistoryCategory | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[WalletHistoryTransaction, str]:
    """Fetch decoded wallet history through Moralis cursor pagination.

    Args:
      address: Wallet address.
      chain: Moralis EVM chain identifier.
      from_date: Inclusive lower timestamp bound accepted by Moralis.
      to_date: Inclusive upper timestamp bound accepted by Moralis.
      from_block: Inclusive lower block bound.
      to_block: Inclusive upper block bound.
      cursor: Initial Moralis pagination cursor.
      limit: Maximum page size.
      order: Sort order.
      include_internal_transactions: Include decoded internal transactions.
      nft_metadata: Include NFT metadata.
      category: Moralis transaction category filter.
      validate: Per-call response validation override.

    Returns:
      A paginated response yielding transaction pages and awaitable as all transactions.

    References:
      Upstream docs: https://docs.moralis.com/web3-data-api/evm/reference/wallet-api/get-wallet-history
    """
    async def next_page(state: str) -> tuple[list[WalletHistoryTransaction], str | None]:
      page = await self.history(
        address,
        chain=chain,
        from_date=from_date,
        to_date=to_date,
        from_block=from_block,
        to_block=to_block,
        cursor=state or None,
        limit=limit,
        order=order,
        include_internal_transactions=include_internal_transactions,
        nft_metadata=nft_metadata,
        category=category,
        validate=validate,
      )
      return page['result'], page.get('cursor')

    return PaginatedResponse(cursor or '', next_page)
