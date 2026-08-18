"""`GET /v5/market/fee-group-info` — Get Fee Group Structure."""

from typing_extensions import Literal, TypedDict
from bybit.core import Endpoint, validator


class MarketMakerFeeTier(TypedDict):
  """One market maker fee tier."""

  level: str
  """Tier name, for example `MM 1`."""
  makerRebate: str
  """Maker rebate of the tier, as a negative ratio."""


class ProFeeTier(TypedDict):
  """One Pro fee tier."""

  level: str
  """Tier name, for example `Pro 1`."""
  takerFeeRate: str
  """Taker fee rate of the tier, as a ratio."""
  makerFeeRate: str
  """Maker fee rate of the tier, as a ratio."""


class FeeRates(TypedDict):
  """Fee tiers offered on the group."""

  pro: list[ProFeeTier]
  """Pro tiers, charging a taker and a maker rate."""
  marketMaker: list[MarketMakerFeeTier]
  """Market maker tiers, paying a maker rebate."""


class FeeGroup(TypedDict):
  """One derivatives fee group."""

  groupName: str
  """Display name of the group."""
  weightingFactor: int
  """Weighting multiplier applied to the group."""
  symbolsNumbers: int
  """Number of contracts in the group."""
  symbols: list[str]
  """Contracts belonging to the group."""
  feeRates: FeeRates
  updateTime: str
  """Time the group was last updated, as a millisecond timestamp."""


class FeeGroupInfo(TypedDict):
  """Derivatives fee groups."""

  list: list[FeeGroup]
  """Fee groups."""


adapter = validator[FeeGroupInfo](FeeGroupInfo)


class FeeGroupEndpoint(Endpoint):
  """`Get Fee Group Structure` — mixed into the router that owns `market.fee_group`."""

  async def fee_group(
    self,
    *,
    product_type: Literal['contract'],
    group_id: Literal['1', '2', '3', '4', '5', '6', '7', '8', '9'] | None = None,
    validate: bool | None = None,
  ) -> FeeGroupInfo:
    """Get the derivatives fee groups: which contracts belong to each group, and the taker, maker and market maker rates of every tier inside it.

    Args:
      product_type: Product family the fee groups apply to.
      group_id: Fee group identifier. Omit to return every group.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/fee-group-info)
    """
    params: dict = {
      'productType': product_type,
    }
    if group_id is not None:
      params['groupId'] = group_id
    r = await self.request('GET', '/v5/market/fee-group-info', params=params)
    return self.result(r, adapter, validate)
