from json import dumps
from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SubGroupSubAccountDetail(TypedDict):
  """Detail for one sub-account within a sub-group."""

  accountId: NotRequired[int]
  """Sub-account ID."""
  accountEmail: NotRequired[str]
  """Sub-account email address."""
  accountAsset: NotRequired[str]
  """Sub-account total assets, in USD value."""
  accountDailySpotVol: NotRequired[str]
  """Sub-account spot trading volume over the trailing 24 hours."""
  accountDailyFutVol: NotRequired[str]
  """Sub-account futures trading volume over the trailing 24 hours."""
  account30dSpotVol: NotRequired[str]
  """Sub-account spot trading volume over the trailing 30 days."""
  account30dFutVol: NotRequired[str]
  """Sub-account futures trading volume over the trailing 30 days."""


class SubGroupDetail(TypedDict):
  """Detail for one sub-group under the master account."""

  groupId: NotRequired[int]
  """Sub-group ID."""
  groupName: NotRequired[str]
  """Name of the sub-group."""
  accountLimit: NotRequired[int]
  """Maximum number of sub-accounts the sub-group may hold."""
  tradeLevel: NotRequired[int]
  """Trading level of the sub-group."""
  feeTier: NotRequired[int]
  """Fee tier of the sub-group."""
  groupAssets: NotRequired[str]
  """Total assets across the sub-group, in USD value."""
  group30dSpotVol: NotRequired[str]
  """Sub-group spot trading volume over the trailing 30 days."""
  group30dFutVol: NotRequired[str]
  """Sub-group futures trading volume over the trailing 30 days."""
  subAccounts: NotRequired[list[SubGroupSubAccountDetail]]
  """Sub-accounts belonging to this sub-group."""


class SubGroupDetails(TypedDict):
  """Sub-group details, including trading volume, fee tiers, and per-sub-account breakdown."""

  status: NotRequired[str]
  """Response status, e.g. `OK`."""
  type: NotRequired[str]
  """Response category, e.g. `GENERAL`."""
  code: NotRequired[str]
  """Response code; `"000000000"` on success."""
  data: NotRequired[list[SubGroupDetail]]
  """One entry per queried (or active) sub-group."""


class SubgroupDetail(RpcEndpoint):
  """Return sub-group information including trading volume, fee tiers, and sub-account details."""

  async def subgroup_detail(
    self,
    *,
    group_id: list[int] | None = None,
    validate: bool | None = None,
  ) -> SubGroupDetails:
    """Return sub-group information including trading volume, fee tiers, and sub-account details.

    Args:
      group_id: Sub-group IDs to query, up to 50. Sent as repeated `groupId` query params, e.g. `groupId=1001&groupId=1002`. Omit to query all active groups.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-link-plus/api/rest-api/~#query-sub-groups-details)
    """
    params = {}
    if group_id is not None:
      params['groupId'] = dumps(group_id, separators=(',', ':'))
    _Response = SubGroupDetails
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/vip/link-plus/subgroups/detail',
      params=params,
      validator=_validator,
      validate=validate,
    )
