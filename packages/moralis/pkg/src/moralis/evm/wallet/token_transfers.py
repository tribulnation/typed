from typing_extensions import NotRequired, Required, TypedDict
from pydantic import TypeAdapter

from typed_core import PaginatedResponse
from moralis.core import Chain, Direction, Endpoint, Order, clean_params

class TokenTransfer(TypedDict, total=False):
  """ERC20 transfer involving a wallet."""
  token_name: str | None
  """Token name."""
  token_symbol: str | None
  """Token symbol."""
  token_logo: str | None
  """Token logo URL."""
  token_decimals: str | None
  """Token decimal precision."""
  from_address_entity: str | None
  """Sender entity label."""
  from_address_entity_logo: str | None
  """Sender entity logo URL."""
  from_address: str | None
  """Sender address."""
  from_address_label: str | None
  """Sender address label."""
  to_address_entity: str | None
  """Recipient entity label."""
  to_address_entity_logo: str | None
  """Recipient entity logo URL."""
  to_address: str | None
  """Recipient address."""
  to_address_label: str | None
  """Recipient address label."""
  address: Required[str]
  """Token contract address."""
  block_hash: str
  """Block hash."""
  block_number: str
  """Block number."""
  block_timestamp: str
  """Block timestamp in upstream format."""
  transaction_hash: str
  """Transaction hash."""
  transaction_index: int
  """Transaction index in the block."""
  log_index: int
  """Transfer log index."""
  value: Required[str]
  """Raw integer transfer amount."""
  value_decimal: str | None
  """Human-readable decimal transfer amount."""
  possible_spam: bool
  """Whether Moralis marks the token as possible spam."""
  verified_contract: bool
  """Whether Moralis marks the token contract as verified."""
  direction: NotRequired[Direction]
  """Wallet-relative transfer direction, when provided."""
  security_score: int | None
  """Moralis token security score."""


class TokenTransfersResponse(TypedDict, total=False):
  """Moralis ERC20 transfer page."""
  page: int
  """Page number."""
  page_size: int
  """Number of transfers returned."""
  cursor: str | None
  """Cursor for the next page."""
  result: Required[list[TokenTransfer]]
  """ERC20 transfers in this page."""

token_transfers_adapter = TypeAdapter(TokenTransfersResponse)

class TokenTransfers(Endpoint):
  """Moralis EVM wallet ERC20 transfer endpoints."""
  async def token_transfers(
    self, address: str, /, *,
    chain: Chain,
    from_date: str | None = None,
    to_date: str | None = None,
    from_block: int | None = None,
    to_block: int | None = None,
    cursor: str | None = None,
    limit: int | None = None,
    order: Order | None = None,
    validate: bool | None = None,
  ) -> TokenTransfersResponse:
    """Fetch ERC20 transfers for a wallet.

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
      validate: Per-call response validation override.

    Returns:
      A page of ERC20 transfers involving the wallet.

    References:
      Upstream docs: https://docs.moralis.com/web3-data-api/evm/reference/wallet-api/get-erc20-transfers-by-wallet
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
    })
    response = await self.request('GET', f'/{address}/erc20/transfers', params=params)
    if self.should_validate(validate):
      return token_transfers_adapter.validate_json(response.text)
    return response.json()

  def token_transfers_paged(
    self, address: str, /, *,
    chain: Chain,
    from_date: str | None = None,
    to_date: str | None = None,
    from_block: int | None = None,
    to_block: int | None = None,
    cursor: str | None = None,
    limit: int | None = None,
    order: Order | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[TokenTransfer, str]:
    """Fetch ERC20 transfers through Moralis cursor pagination.

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
      validate: Per-call response validation override.

    Returns:
      A paginated response yielding transfer pages and awaitable as all transfers.
    """
    async def next_page(state: str) -> tuple[list[TokenTransfer], str | None]:
      page = await self.token_transfers(
        address,
        chain=chain,
        from_date=from_date,
        to_date=to_date,
        from_block=from_block,
        to_block=to_block,
        cursor=state or None,
        limit=limit,
        order=order,
        validate=validate,
      )
      return page['result'], page.get('cursor')

    return PaginatedResponse(cursor or '', next_page)
