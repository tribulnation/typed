"""Moralis EVM wallet token balance endpoint."""

from pydantic import TypeAdapter
from typed_core import PaginatedResponse
from typing_extensions import Required, Sequence, TypedDict

from moralis.core import Chain, Endpoint, clean_params


class TokenBalance(TypedDict, total=False):
  """Token balance in a wallet snapshot."""
  token_address: Required[str]
  """Token contract address, or the Moralis native-token sentinel."""
  symbol: str | None
  """Token symbol."""
  name: str | None
  """Token name."""
  logo: str | None
  """Token logo URL."""
  thumbnail: str | None
  """Token thumbnail URL."""
  decimals: int
  """Token decimal precision."""
  balance: Required[str]
  """Raw integer balance."""
  possible_spam: bool
  """Whether Moralis marks the token as possible spam."""
  verified_contract: bool
  """Whether Moralis marks the token contract as verified."""
  total_supply: str | None
  """Raw total supply, when provided."""
  total_supply_formatted: str | None
  """Human-readable total supply, when provided."""
  percentage_relative_to_total_supply: float | None
  """Balance percentage relative to total supply."""
  security_score: int | None
  """Moralis token security score."""
  balance_formatted: str
  """Human-readable balance."""
  usd_price: float | None
  """Token USD price, when included."""
  usd_price_24hr_percent_change: float | None
  """Token USD price percent change over the previous 24 hours."""
  usd_price_24hr_usd_change: float | None
  """Token USD price absolute change over the previous 24 hours."""
  usd_value: float | None
  """Balance USD value, when included."""
  usd_value_24hr_usd_change: float | None
  """Balance USD value absolute change over the previous 24 hours."""
  native_token: bool
  """Whether this entry represents the chain native token."""
  portfolio_percentage: float | None
  """Token percentage of the wallet portfolio."""


class TokenBalancesResponse(TypedDict, total=False):
  """Moralis token balance page."""
  cursor: str | None
  """Cursor for the next page."""
  page: int
  """Page number."""
  page_size: int
  """Number of balances returned."""
  block_number: int
  """Block number for the snapshot."""
  result: Required[list[TokenBalance]]
  """Token balances in this page."""


token_balances_adapter = TypeAdapter(TokenBalancesResponse)


class TokenBalances(Endpoint):
  """Moralis EVM wallet token balance endpoints."""

  async def token_balances(
    self, address: str, /, *,
    chain: Chain,
    to_block: int | None = None,
    token_addresses: Sequence[str] | None = None,
    exclude_spam: bool | None = None,
    exclude_unverified_contracts: bool | None = None,
    exclude_native: bool | None = None,
    max_token_inactivity: float | None = None,
    min_pair_side_liquidity_usd: float | None = None,
    cursor: str | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> TokenBalancesResponse:
    """Fetch ERC20 and native token balances for a wallet.

    Args:
      address: Wallet address.
      chain: Moralis EVM chain identifier.
      to_block: Block number at which balances should be checked.
      token_addresses: Token contracts to restrict the balance query.
      exclude_spam: Exclude tokens Moralis marks as possible spam.
      exclude_unverified_contracts: Exclude unverified token contracts.
      exclude_native: Exclude the native gas-token balance.
      max_token_inactivity: Exclude tokens inactive for more than this number of days.
      min_pair_side_liquidity_usd: Exclude tokens below this pair-side liquidity threshold.
      cursor: Moralis pagination cursor.
      limit: Maximum page size.
      validate: Per-call response validation override.

    Returns:
      A page of wallet token balances.

    References:
      Upstream docs: https://docs.moralis.com/web3-data-api/evm/reference/wallet-api/get-wallet-token-balances
    """
    params = clean_params({
      'chain': chain,
      'to_block': to_block,
      'token_addresses': token_addresses,
      'exclude_spam': exclude_spam,
      'exclude_unverified_contracts': exclude_unverified_contracts,
      'exclude_native': exclude_native,
      'max_token_inactivity': max_token_inactivity,
      'min_pair_side_liquidity_usd': min_pair_side_liquidity_usd,
      'cursor': cursor,
      'limit': limit,
    })
    response = await self.request('GET', f'/wallets/{address}/tokens', params=params)
    if self.should_validate(validate):
      return token_balances_adapter.validate_json(response.text)
    return response.json()

  def token_balances_paged(
    self, address: str, /, *,
    chain: Chain,
    to_block: int | None = None,
    token_addresses: Sequence[str] | None = None,
    exclude_spam: bool | None = None,
    exclude_unverified_contracts: bool | None = None,
    exclude_native: bool | None = None,
    max_token_inactivity: float | None = None,
    min_pair_side_liquidity_usd: float | None = None,
    cursor: str | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[TokenBalance, str]:
    """Fetch token balances through Moralis cursor pagination.

    Args:
      address: Wallet address.
      chain: Moralis EVM chain identifier.
      to_block: Block number at which balances should be checked.
      token_addresses: Token contracts to restrict the balance query.
      exclude_spam: Exclude tokens Moralis marks as possible spam.
      exclude_unverified_contracts: Exclude unverified token contracts.
      exclude_native: Exclude the native gas-token balance.
      max_token_inactivity: Exclude tokens inactive for more than this number of days.
      min_pair_side_liquidity_usd: Exclude tokens below this pair-side liquidity threshold.
      cursor: Initial Moralis pagination cursor.
      limit: Maximum page size.
      validate: Per-call response validation override.

    Returns:
      A paginated response yielding balance pages and awaitable as all balances.
    """
    async def next_page(state: str) -> tuple[list[TokenBalance], str | None]:
      page = await self.token_balances(
        address,
        chain=chain,
        to_block=to_block,
        token_addresses=token_addresses,
        exclude_spam=exclude_spam,
        exclude_unverified_contracts=exclude_unverified_contracts,
        exclude_native=exclude_native,
        max_token_inactivity=max_token_inactivity,
        min_pair_side_liquidity_usd=min_pair_side_liquidity_usd,
        cursor=state or None,
        limit=limit,
        validate=validate,
      )
      return page['result'], page.get('cursor')

    return PaginatedResponse(cursor or '', next_page)
