from pydantic import TypeAdapter
from typing_extensions import Literal, Required, Sequence, TypedDict

from moralis.core import Endpoint, clean_params

TokenMetadataChain = Literal[
  'eth',
  '0x1',
  'sepolia',
  '0xaa36a7',
  'polygon',
  '0x89',
  'bsc',
  '0x38',
  'bsc testnet',
  '0x61',
  'avalanche',
  '0xa86a',
  'fantom',
  '0xfa',
  'cronos',
  '0x19',
  'arbitrum',
  '0xa4b1',
  'chiliz',
  '0x15b38',
  'chiliz testnet',
  '0x15b32',
  'gnosis',
  '0x64',
  'gnosis testnet',
  '0x27d8',
  'base',
  '0x2105',
  'base sepolia',
  '0x14a34',
  'optimism',
  '0xa',
  'polygon amoy',
  '0x13882',
  'linea',
  '0xe708',
  'moonbeam',
  '0x504',
  'moonriver',
  '0x505',
  'moonbase',
  '0x507',
  'linea sepolia',
  '0xe705',
  'flow',
  '0x2eb',
  'flow-testnet',
  '0x221',
  'ronin',
  '0x7e4',
  'ronin-testnet',
  '0x31769',
  'lisk',
  '0x46f',
  'lisk-sepolia',
  '0x106a',
  'pulse',
  '0x171',
  'sei-testnet',
  '0x530',
  'sei',
  '0x531',
  'monad',
  '0x8f',
]
"""Moralis chain identifier accepted by the token metadata endpoint."""


JsonScalar = str | int | float | bool | None
"""Scalar JSON value used for open-ended upstream metadata objects."""


class Erc20TokenMetadata(TypedDict, total=False):
  """ERC20 token metadata returned by Moralis."""
  address: Required[str]
  """Token contract address."""
  address_label: str | None
  """Moralis address label, when available."""
  name: Required[str]
  """Token name."""
  symbol: Required[str]
  """Token symbol."""
  decimals: Required[str]
  """Token decimal precision in upstream string format."""
  logo: str | None
  """Token logo URL."""
  logo_hash: str | None
  """Hash of the token logo, when available."""
  thumbnail: str | None
  """Token thumbnail URL."""
  total_supply: str | None
  """Raw integer total supply, when available."""
  total_supply_formatted: str | None
  """Human-readable total supply, when available."""
  fully_diluted_valuation: str | None
  """Fully diluted valuation in upstream string format."""
  block_number: int | str | None
  """Block number associated with the metadata snapshot, when available."""
  validated: int | bool | str | None
  """Upstream validation status, when available."""
  created_at: str | None
  """Metadata creation timestamp in upstream format."""
  possible_spam: Required[bool]
  """Whether Moralis marks the token as possible spam."""
  verified_contract: Required[bool]
  """Whether Moralis marks the token contract as verified."""
  categories: Required[list[str]]
  """Moralis token categories."""
  links: Required[dict[str, str | None]]
  """Off-chain token links."""
  security_score: int | None
  """Moralis token security score."""
  description: str | None
  """Token description, when available."""
  circulating_supply: str | None
  """Circulating supply in upstream string format, when available."""
  market_cap: str | None
  """Market capitalization in upstream string format, when available."""
  implementations: Required[list[dict[str, JsonScalar]]]
  """Cross-chain token implementations."""


TokenMetadataResponse = list[Erc20TokenMetadata]
"""Metadata entries for the requested ERC20 token contracts."""

token_metadata_adapter = TypeAdapter(TokenMetadataResponse)

class TokenMetadata(Endpoint):
  """Moralis EVM token metadata endpoints."""

  async def metadata(
    self, *,
    addresses: Sequence[str],
    chain: TokenMetadataChain = 'eth',
    validate: bool | None = None,
  ) -> TokenMetadataResponse:
    """Fetch ERC20 token metadata by contract address.

    Args:
      addresses: Token contract addresses to query. Moralis accepts up to 10.
      chain: Moralis EVM chain identifier.
      validate: Per-call response validation override.

    Returns:
      Metadata entries for the requested ERC20 contracts.

    References:
      Upstream docs: https://docs.moralis.com/data-api/evm/token/metadata/token-metadata
    """
    params = clean_params({
      'chain': chain,
      'addresses': addresses,
    })
    response = await self.request('GET', '/erc20/metadata', params=params)
    if self.should_validate(validate):
      return token_metadata_adapter.validate_json(response.text)
    return response.json()
