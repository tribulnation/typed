"""`spot.earn.allocations` -- private Spot endpoint."""

from datetime import datetime
from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class EarnAllocationAmountValue0(TypedDict):
  native: NotRequired[str]
  """Amount in the native asset."""
  converted: NotRequired[str]
  """Amount converted into the requested asset."""


class EarnAllocationAmountValueAccumulatedReward(TypedDict):
  """Reward accumulated in the payout period so far."""

  native: NotRequired[str]
  """Amount in the native asset."""
  converted: NotRequired[str]
  """Amount converted into the requested asset."""


class EarnAllocationAmountValueEstimatedReward(TypedDict):
  """Estimated reward from now until the payout."""

  native: NotRequired[str]
  """Amount in the native asset."""
  converted: NotRequired[str]
  """Amount converted into the requested asset."""


class EarnAllocationAmountValueTotal(TypedDict):
  """Total amount allocated to this Earn strategy, across every state."""

  native: NotRequired[str]
  """Amount in the native asset."""
  converted: NotRequired[str]
  """Amount converted into the requested asset."""


class EarnAllocationAmountValueTotalRewarded(TypedDict):
  """Amount earned using this strategy over the account's whole lifetime."""

  native: NotRequired[str]
  """Amount in the native asset."""
  converted: NotRequired[str]
  """Amount converted into the requested asset."""


class EarnAllocationEntryBondingAnyOf0AllocationsItem(TypedDict):
  """One individual allocation contributing to a bonding/exit-queue/unbonding state, and when it transitions to the next state."""

  created_at: NotRequired[datetime]
  """When the request that created this allocation (allocate, or deallocate for exit-queue/unbonding) was received and processed."""
  expires: NotRequired[datetime]
  """When these funds finish unbonding. For `exit_queue`, this is the unbonding completion time, not the time the funds leave the exit queue."""
  native: NotRequired[str]
  """Amount in the native asset."""
  converted: NotRequired[str]
  """Amount converted into the requested asset."""


class EarnAllocationEntryExitQueueAnyOf0AllocationsItem(TypedDict):
  """One individual allocation contributing to a bonding/exit-queue/unbonding state, and when it transitions to the next state."""

  created_at: NotRequired[datetime]
  """When the request that created this allocation (allocate, or deallocate for exit-queue/unbonding) was received and processed."""
  expires: NotRequired[datetime]
  """When these funds finish unbonding. For `exit_queue`, this is the unbonding completion time, not the time the funds leave the exit queue."""
  native: NotRequired[str]
  """Amount in the native asset."""
  converted: NotRequired[str]
  """Amount converted into the requested asset."""


class EarnAllocationEntryUnbondingAnyOf0AllocationsItem(TypedDict):
  """One individual allocation contributing to a bonding/exit-queue/unbonding state, and when it transitions to the next state."""

  created_at: NotRequired[datetime]
  """When the request that created this allocation (allocate, or deallocate for exit-queue/unbonding) was received and processed."""
  expires: NotRequired[datetime]
  """When these funds finish unbonding. For `exit_queue`, this is the unbonding completion time, not the time the funds leave the exit queue."""
  native: NotRequired[str]
  """Amount in the native asset."""
  converted: NotRequired[str]
  """Amount converted into the requested asset."""


class EarnAllocationPayout(TypedDict):
  period_start: NotRequired[datetime]
  """When the current payout period started -- either the last payout date or when it was enabled."""
  period_end: NotRequired[datetime]
  """Tentative date of the next reward payout."""
  accumulated_reward: NotRequired[EarnAllocationAmountValueAccumulatedReward]
  estimated_reward: NotRequired[EarnAllocationAmountValueEstimatedReward]


class EarnAllocationStateBondingAnyOf0(TypedDict):
  """Amount allocated in one transitional state (bonding, exit-queue, or unbonding), with the individual allocations composing it."""

  allocation_count: NotRequired[int]
  """Number of individual allocations in this state for this asset."""
  allocations: NotRequired[list[EarnAllocationEntryBondingAnyOf0AllocationsItem]]
  """Individual allocations composing this state, and when each expires into the next."""
  native: NotRequired[str]
  """Total amount in this state, in the native asset."""
  converted: NotRequired[str]
  """Total amount in this state, converted into the requested asset."""


class EarnAllocationStateExitQueueAnyOf0(TypedDict):
  """Amount allocated in one transitional state (bonding, exit-queue, or unbonding), with the individual allocations composing it."""

  allocation_count: NotRequired[int]
  """Number of individual allocations in this state for this asset."""
  allocations: NotRequired[list[EarnAllocationEntryExitQueueAnyOf0AllocationsItem]]
  """Individual allocations composing this state, and when each expires into the next."""
  native: NotRequired[str]
  """Total amount in this state, in the native asset."""
  converted: NotRequired[str]
  """Total amount in this state, converted into the requested asset."""


class EarnAllocationStateUnbondingAnyOf0(TypedDict):
  """Amount allocated in one transitional state (bonding, exit-queue, or unbonding), with the individual allocations composing it."""

  allocation_count: NotRequired[int]
  """Number of individual allocations in this state for this asset."""
  allocations: NotRequired[list[EarnAllocationEntryUnbondingAnyOf0AllocationsItem]]
  """Individual allocations composing this state, and when each expires into the next."""
  native: NotRequired[str]
  """Total amount in this state, in the native asset."""
  converted: NotRequired[str]
  """Total amount in this state, converted into the requested asset."""


class EarnAllocationAmount(TypedDict):
  """Amounts allocated to this Earn strategy, broken down by state."""

  total: NotRequired[EarnAllocationAmountValueTotal]
  bonding: NotRequired[EarnAllocationStateBondingAnyOf0 | None]
  """Amount in the bonding state. Present only when there are bonding allocations."""
  exit_queue: NotRequired[EarnAllocationStateExitQueueAnyOf0 | None]
  """Amount in the exit-queue state (ETH only). Present only when there are exit-queue allocations."""
  unbonding: NotRequired[EarnAllocationStateUnbondingAnyOf0 | None]
  """Amount in the unbonding state. Present only when there are unbonding allocations."""
  pending: NotRequired[EarnAllocationAmountValue0 | None]
  """Pending (de)allocation amount -- negative when the pending operation is a deallocation. Present only when there is a pending operation."""


class EarnAllocation(TypedDict):
  """The user's allocation to a single Earn strategy."""

  strategy_id: NotRequired[str]
  """Unique ID of the Earn strategy."""
  native_asset: NotRequired[str]
  """The native asset of this allocation."""
  amount_allocated: NotRequired[EarnAllocationAmount]
  total_rewarded: NotRequired[EarnAllocationAmountValueTotalRewarded]
  payout: NotRequired[EarnAllocationPayout | None]
  """Information about the current payout period. Absent when there is no current payout period."""
  asset_class: NotRequired[str]
  """Asset class of native_asset, e.g. `currency`. Confirmed present live, not in upstream's own published field list."""
  is_utilized: NotRequired[bool]
  """Whether this allocation is actively earning rewards. Confirmed present live, not in upstream's own published field list."""


class EarnAllocationsResult(TypedDict):
  """The user's Earn allocations across all strategies."""

  converted_asset: NotRequired[str]
  """The secondary asset used to show the value of allocations, as chosen in the request."""
  converted_asset_class: NotRequired[str]
  """Asset class of `converted_asset`, e.g. `currency`. Confirmed present live, not in upstream's own published field list."""
  next_cursor: NotRequired[str | None]
  """Cursor for the next page. Present as `null` on a live call even though upstream's own response schema doesn't declare it (only its worked example does, likely copied from `Strategies`); see `notes` -- paging is not documented as implemented for this endpoint either."""
  total_allocated: NotRequired[str]
  """Total amount allocated across all strategies, denominated in `converted_asset`."""
  total_rewarded: NotRequired[str]
  """Amount earned across all strategies over the account's lifetime, denominated in `converted_asset`."""
  items: NotRequired[list[EarnAllocation]]
  """One entry per strategy the user has (or has had) an allocation in."""


validate_allocations = validator(EarnAllocationsResult)


class Allocations(RpcEndpoint):
  """`spot.earn.allocations`."""

  async def allocations(
    self,
    *,
    ascending: bool | None = None,
    converted_asset: str | None = None,
    hide_zero_allocations: bool | None = None,
  ) -> EarnAllocationsResult:
    """List all allocations for the user.

    Requires the `Query Funds` API key permission.

    By default all allocations are returned, even for strategies that have been used in the past and now have zero balance, so the user can see how much was earned with a given strategy historically. `hide_zero_allocations` removes zero-balance entries from the output. Paging hasn't been implemented for this method, as the result for a particular user isn't expected to be overwhelmingly large.

    All amounts in the output can be denominated in a currency of the user's choice (the `converted_asset` parameter). Information about when the next reward will be paid is also provided.

    Allocated funds can be in up to 4 states: `bonding`, `allocated`, `exit_queue` (ETH only), `unbonding`. Any funds in `total` not in `bonding`/`unbonding` are simply allocated and earning rewards; whether the other states also earn rewards depends on the strategy (see `Earn/Strategies`). ETH in `exit_queue` still earns rewards.

    For ETH, when funds are in `exit_queue`, the `expires` time given is when the funds finish unbonding, not when they leave the exit queue for unbonding.

    (Un)bonding time estimates can be inaccurate immediately after (de)allocating; wait 1-2 minutes for an accurate result.

    Args:
      ascending: `true` to sort ascending, `false` (the default) for descending.
      converted_asset: A secondary currency to express the value of allocations in. Defaults to USD.
      hide_zero_allocations: Omit entries for strategies used in the past that now hold no allocation. Defaults to `false`.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/earn/list-earn-allocations)
    """
    data = {}
    if ascending is not None:
      data['ascending'] = ascending
    if converted_asset is not None:
      data['converted_asset'] = converted_asset
    if hide_zero_allocations is not None:
      data['hide_zero_allocations'] = hide_zero_allocations

    return await self.authed_request(
      '/0/private/Earn/Allocations', data, validator=validate_allocations
    )
