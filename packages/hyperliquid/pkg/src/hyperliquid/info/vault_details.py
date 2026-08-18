from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class VaultDetailsAction(TypedDict):
  type: Literal['vaultDetails']
  user: NotRequired[str]
  vaultAddress: str


class VaultFollower(TypedDict):
  """A single follower's position in a vault."""

  allTimePnl: str
  """Follower's all-time PnL from following this vault, as a decimal string."""
  daysFollowing: int
  """Number of days the follower has been following this vault."""
  lockupUntil: int
  """Time the follower's current deposit is locked until, in milliseconds since epoch."""
  pnl: str
  """Follower's PnL since their current vault entry, as a decimal string."""
  user: str
  """Address of the follower, in 42-character hexadecimal format."""
  vaultEntryTime: int
  """Time the follower entered the vault, in milliseconds since epoch."""
  vaultEquity: str
  """Follower's current equity in the vault, as a decimal string."""


class VaultParentRelationshipData(TypedDict):
  """Data specific to a parent vault relationship."""

  childAddresses: list[str]
  """Addresses of the vaults this vault is the parent of."""


class VaultPortfolioMetrics(TypedDict):
  """Performance metrics for a vault over a single reporting period."""

  accountValueHistory: list[tuple[int, str]]
  """Time series of the vault's account value over the period."""
  pnlHistory: list[tuple[int, str]]
  """Time series of the vault's cumulative PnL over the period."""
  vlm: str
  """Trading volume over the period, as a decimal string."""


class VaultParentRelationship(TypedDict):
  """This vault's relationship to other vaults, when it participates in a parent/child structure."""

  data: VaultParentRelationshipData
  type: Literal['parent']
  """Kind of vault relationship."""


class VaultDetails(TypedDict):
  """Details for a single vault."""

  allowDeposits: bool
  """Whether the vault currently accepts new deposits."""
  alwaysCloseOnWithdraw: bool
  """Whether a withdrawal always fully closes the withdrawer's position rather than partially reducing it."""
  apr: float
  """Annualized rate of return of the vault."""
  description: str
  """Free-text description of the vault, as set by its leader."""
  followerState: None
  """The querying `user`'s own follower state in this vault. Documented and observed as `null` in every captured example; no non-null shape has been confirmed."""
  followers: list[VaultFollower]
  """Current followers of the vault."""
  isClosed: bool
  """Whether the vault is closed to further activity."""
  leader: str
  """Address of the vault's leader, in 42-character hexadecimal format."""
  leaderCommission: int
  """Commission the leader takes from followers' profits, in basis points."""
  leaderFraction: float
  """Fraction of the vault's equity owned by the leader."""
  maxDistributable: float
  """Maximum amount currently distributable from the vault."""
  maxWithdrawable: float
  """Maximum amount the querying `user` can currently withdraw from the vault."""
  name: str
  """Display name of the vault, as set by its leader."""
  portfolio: list[
    tuple[
      Literal[
        'allTime',
        'day',
        'month',
        'perpAllTime',
        'perpDay',
        'perpMonth',
        'perpWeek',
        'week',
      ],
      VaultPortfolioMetrics,
    ]
  ]
  """The vault's performance metrics, one entry per reporting period."""
  relationship: VaultParentRelationship
  """This vault's relationship to other vaults. Only the `parent` shape is documented and observed; a standalone or `child` vault's shape has not been confirmed."""
  vaultAddress: str
  """Address of the vault, in 42-character hexadecimal format."""


adapter = pydantic.TypeAdapter(VaultDetails | None)


class VaultDetailsEndpoint(InfoMixin):
  async def vault_details(
    self,
    *,
    user: str | None = None,
    vault_address: str,
  ) -> VaultDetails | None:
    """Retrieve details for a vault -- its leader, followers, performance history, and current state -- through Hyperliquid POST /info using request type `vaultDetails`. Returns `null` when `vaultAddress` does not correspond to an existing vault.

    Args:
      user: Address to evaluate follower-specific fields (e.g. `maxWithdrawable`) for, in 42-character hexadecimal format.
      vault_address: Address of the vault to query, in 42-character hexadecimal format.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: VaultDetailsAction = {
      'type': 'vaultDetails',
      'vaultAddress': vault_address,
    }
    if user is not None:
      params['user'] = user
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
