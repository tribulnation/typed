from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class TokenDetailsAction(TypedDict):
  type: Literal['tokenDetails']
  tokenId: str


class TokenGenesis(TypedDict):
  """Genesis allocation recorded at token deployment."""

  userBalances: list[tuple[str, str]]
  """Balances allocated to addresses at genesis."""
  existingTokenBalances: list[tuple[int, str]]
  """Balances carried over from already-deployed tokens at genesis."""


class TokenDetails(TypedDict):
  """Genesis, supply, and pricing details for a spot token."""

  name: str
  """Token symbol / display name."""
  maxSupply: str
  """Maximum token supply, as a decimal string."""
  totalSupply: str
  """Current total token supply, as a decimal string."""
  circulatingSupply: str
  """Current circulating token supply, as a decimal string."""
  szDecimals: int
  """Number of decimals used for order sizes of this token."""
  weiDecimals: int
  """Number of decimals used for the token's smallest onchain (wei) unit."""
  midPx: str
  """Current mid price of the token in USD, as a decimal string."""
  markPx: str
  """Current mark price of the token in USD, as a decimal string."""
  prevDayPx: str
  """Mark price of the token in USD 24 hours before the current one, as a decimal string."""
  genesis: TokenGenesis | None
  """Genesis allocation for the token, or null if it wasn't deployed with one."""
  deployer: str | None
  """Onchain address that deployed the token, or null if unknown."""
  deployGas: str | None
  """Gas paid to deploy the token, as a decimal string, or null if unknown."""
  deployTime: str | None
  """Timestamp the token was deployed, or null if unknown."""
  seededUsdc: str
  """Amount of USDC seeded into the token's hyperliquidity at deploy, as a decimal string."""
  nonCirculatingUserBalances: list[tuple[str, str]]
  """Balances excluded from the token's circulating supply."""
  futureEmissions: str
  """Scheduled future token emissions, as a decimal string."""


adapter = pydantic.TypeAdapter(TokenDetails)


class TokenDetailsEndpoint(InfoMixin):
  async def token_details(self, *, token_id: str) -> TokenDetails:
    """Look up genesis allocation, supply, and pricing details for a single spot token by its onchain token id.

    Args:
      token_id: Onchain token id, as a 34-character hex string.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot)
    """
    params: TokenDetailsAction = {
      'type': 'tokenDetails',
      'tokenId': token_id,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
