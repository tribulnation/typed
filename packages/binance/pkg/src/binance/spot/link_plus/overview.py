from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


LinkPlusOverviewDataKeywords = TypedDict(
  'LinkPlusOverviewDataKeywords',
  {'30dSpotVol': NotRequired[str], '30dFutVol': NotRequired[str]},
)
"""
  - `30dSpotVol`: Total spot trading volume across all sub-groups over the trailing 30 days.
  - `30dFutVol`: Total futures trading volume across all sub-groups over the trailing 30 days.
"""


class LinkPlusOverviewData(LinkPlusOverviewDataKeywords):
  """Master-account-wide Link Plus totals across all sub-groups."""

  vipLevel: NotRequired[int]
  """VIP level of the master account."""
  bnbHold: NotRequired[str]
  """Amount of BNB held by the master account toward VIP fee benefits."""
  totalGroups: NotRequired[int]
  """Total number of sub-groups under the master account."""
  groupLimit: NotRequired[int]
  """Maximum number of sub-groups the master account may create."""
  totalAssets: NotRequired[str]
  """Total assets across all sub-groups, in USD value."""


class LinkPlusOverview(TypedDict):
  """Master account Link Plus overview."""

  status: NotRequired[str]
  """Response status, e.g. `OK`."""
  type: NotRequired[str]
  """Response category, e.g. `GENERAL`."""
  code: NotRequired[str]
  """Response code; `"000000000"` on success."""
  data: NotRequired[LinkPlusOverviewData]


class Overview(RpcEndpoint):
  """Return master account information for all sub-groups, including total number of groups, total trading volumes, and total assets."""

  async def overview(self, *, validate: bool | None = None) -> LinkPlusOverview:
    """Return master account information for all sub-groups, including total number of groups, total trading volumes, and total assets.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-link-plus/api/rest-api/~#query-link-plus-overview)
    """
    _Response = LinkPlusOverview
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/vip/link-plus/overview', validator=_validator, validate=validate
    )
