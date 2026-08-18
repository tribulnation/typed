from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class LiquidatedPosition(TypedDict):
  """One position closed by a liquidation ledger entry."""

  coin: str
  """Perp coin symbol of the liquidated position."""
  szi: str
  """Signed size of the liquidated position."""


class UserNonFundingLedgerUpdatesSubscription(TypedDict):
  """Subscription parameters that were acknowledged."""

  type: Literal['userNonFundingLedgerUpdates']
  """Subscription channel identifier."""
  user: str
  """The account address whose activity this subscription tracks."""


class UserNonFundingLedgerUpdatesSubscriptionParams(TypedDict):
  """Identifies the account whose non-funding ledger events to subscribe to."""

  user: str
  """The account address whose activity this subscription tracks."""


class WsAccountClassTransfer(TypedDict):
  """A transfer between an account's perp and spot wallets."""

  type: Literal['accountClassTransfer']
  """Ledger entry kind discriminator."""
  usdc: str
  """USDC amount moved between the account's perp and spot wallets."""
  toPerp: bool
  """True when the transfer moved funds from spot to perp; false for perp to spot."""


class WsDeposit(TypedDict):
  """A USDC deposit onto the venue."""

  type: Literal['deposit']
  """Ledger entry kind discriminator."""
  usdc: str
  """Amount deposited, in USDC."""


class WsInternalTransfer(TypedDict):
  """A direct USDC transfer between two accounts."""

  type: Literal['internalTransfer']
  """Ledger entry kind discriminator."""
  usdc: str
  """Amount transferred, in USDC."""
  user: str
  """Sending account address."""
  destination: str
  """Receiving account address."""
  fee: str
  """Transfer fee, in USDC."""


class WsRewardsClaim(TypedDict):
  """A rewards claim ledger entry."""

  type: Literal['rewardsClaim']
  """Ledger entry kind discriminator."""
  amount: str
  """Amount of rewards claimed."""


class WsSpotGenesis(TypedDict):
  """A spot token genesis credit ledger entry."""

  type: Literal['spotGenesis']
  """Ledger entry kind discriminator."""
  token: str
  """Spot token symbol credited by genesis."""
  amount: str
  """Token amount credited."""


class WsSpotTransfer(TypedDict):
  """A spot token transfer between two accounts."""

  type: Literal['spotTransfer']
  """Ledger entry kind discriminator."""
  token: str
  """Spot token symbol transferred."""
  amount: str
  """Token amount transferred."""
  usdcValue: str
  """USDC value of the transferred amount at transfer time."""
  user: str
  """Sending account address."""
  destination: str
  """Receiving account address."""
  fee: str
  """Transfer fee, in USDC."""


class WsSubAccountTransfer(TypedDict):
  """A USDC transfer between a master account and one of its sub-accounts."""

  type: Literal['subAccountTransfer']
  """Ledger entry kind discriminator."""
  usdc: str
  """Amount transferred, in USDC."""
  user: str
  """Sending account address."""
  destination: str
  """Receiving sub-account address."""


class WsVaultDelta(TypedDict):
  """A vault creation, deposit, or distribution ledger entry."""

  type: Literal['vaultCreate', 'vaultDeposit', 'vaultDistribution']
  """Ledger entry kind discriminator."""
  vault: str
  """Vault address."""
  usdc: str
  """USDC amount moved by this vault action."""


class WsVaultLeaderCommission(TypedDict):
  """Commission earned by a vault leader."""

  type: Literal['vaultLeaderCommission']
  """Ledger entry kind discriminator."""
  user: str
  """Vault leader's account address."""
  usdc: str
  """Commission earned, in USDC."""


class WsVaultWithdrawal(TypedDict):
  """A vault withdrawal ledger entry."""

  type: Literal['vaultWithdraw']
  """Ledger entry kind discriminator."""
  vault: str
  """Vault address."""
  user: str
  """Withdrawing depositor's account address."""
  requestedUsd: str
  """USD amount originally requested for withdrawal."""
  commission: str
  """Commission paid to the vault leader."""
  closingCost: str
  """Cost incurred closing positions to fund the withdrawal."""
  basis: str
  """Cost basis of the withdrawn deposit."""
  netWithdrawnUsd: str
  """USD amount actually paid out after commission and closing cost."""


class WsWithdraw(TypedDict):
  """A USDC withdrawal from the venue."""

  type: Literal['withdraw']
  """Ledger entry kind discriminator."""
  usdc: str
  """Amount withdrawn, in USDC."""
  nonce: int
  """Nonce used to authorize the withdrawal."""
  fee: str
  """Withdrawal fee, in USDC."""


class UserNonFundingLedgerUpdatesSubscribeAck(TypedDict):
  """Echo of the subscription that was acknowledged."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: UserNonFundingLedgerUpdatesSubscription


class WsLedgerLiquidation(TypedDict):
  """A liquidation ledger entry."""

  type: Literal['liquidation']
  """Ledger entry kind discriminator."""
  accountValue: str
  """Account value at liquidation time (the isolated position's own value, for an isolated position)."""
  leverageType: Literal['Cross', 'Isolated']
  """Margin mode of the liquidated position(s)."""
  liquidatedPositions: list[LiquidatedPosition]
  """Positions closed by this liquidation."""


class WsUserNonFundingLedgerUpdate(TypedDict):
  """One non-funding ledger entry: a deposit, withdrawal, transfer, liquidation, or vault/rewards event."""

  time: int
  """Millisecond epoch timestamp when the ledger event occurred."""
  hash: str
  """L1 transaction hash of the ledger event."""
  delta: (
    WsDeposit
    | WsWithdraw
    | WsInternalTransfer
    | WsSubAccountTransfer
    | WsLedgerLiquidation
    | WsVaultDelta
    | WsVaultWithdrawal
    | WsVaultLeaderCommission
    | WsSpotTransfer
    | WsAccountClassTransfer
    | WsSpotGenesis
    | WsRewardsClaim
  )
  """One non-funding ledger event, discriminated by its own `type` field."""


class UserNonFundingLedgerUpdatesUpdate(TypedDict):
  """Snapshot or incremental update of the user's non-funding ledger history."""

  isSnapshot: bool
  """True on the initial snapshot message; false on each subsequent streamed update."""
  user: str
  """The account address whose activity this subscription tracks."""
  nonFundingLedgerUpdates: list[WsUserNonFundingLedgerUpdate]
  """Ledger entries in this snapshot or update, oldest first."""


adapter = pydantic.TypeAdapter(UserNonFundingLedgerUpdatesUpdate)


class UserNonFundingLedgerUpdates(StreamsMixin):
  def user_non_funding_ledger_updates(self, user: str):
    """Subscribe to a user's non-funding ledger updates: deposits, withdrawals, transfers, and liquidations, as an initial snapshot followed by streamed events.

    Args:
      user: The account address whose activity this subscription tracks.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._user_non_funding_ledger_updates_impl(user))

  async def _user_non_funding_ledger_updates_impl(self, user: str):
    params: dict[str, object] = {
      'user': user,
    }
    stream = await self.subscribe('userNonFundingLedgerUpdates', params)

    def mapper(msg) -> UserNonFundingLedgerUpdatesUpdate:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
