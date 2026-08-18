from decimal import Decimal
from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class RewardAllowedItem(TypedDict):
  currency: NotRequired[str]
  """Currency where can receive rewards"""
  extraYield: NotRequired[Decimal]
  """Extra Yield by currency applied in the reward"""
  type: NotRequired[Literal['daily', 'weekly', 'monthly']]
  """Reward type"""


class Entry(TypedDict):
  currency: NotRequired[str]
  """Currency symbol, it should be an allowed currency"""
  disabled: NotRequired[bool]
  """Currency status on earn"""
  isNew: NotRequired[bool]
  """Currency added on earn in the last 7 days"""
  currenciesRewardAllowed: NotRequired[list[RewardAllowedItem]]
  """Currency rewards allowed with their info"""
  levelExtraYieldType: NotRequired[Literal['space-pool', 'provided']]
  """Source of the extra yield applied to this asset's level bonus."""


validate_response = validator(list[Entry])


class Assets(RpcEndpoint):
  async def assets(
    self,
    *,
    type: Literal['partner', 'farming-pool'] | None = None,
    validate: bool | None = None,
  ) -> list[Entry]:
    """Retrieves full list of supported assets in earn service

    Args:
      type: Asset type
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/earn/GET/v2/earn/assets)
    """
    params = {'type': type} if type is not None else None
    return await self.request(
      'GET',
      '/v2/earn/assets',
      params=params,
      validator=validate_response,
      validate=validate,
    )
