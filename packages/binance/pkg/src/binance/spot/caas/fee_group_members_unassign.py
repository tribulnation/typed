from json import dumps
from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FeeGroupMemberFailure(TypedDict):
  """A sub-user for which a fee-group membership change failed, with the reason."""

  subUserId: NotRequired[int]
  """Sub-user ID that failed."""
  errorMessage: NotRequired[str]
  """Reason the operation failed for this sub-user."""


class UnassignFeeGroupMembersResult(TypedDict):
  """Outcome of the unassignment, broken down into successes and failures."""

  successCount: NotRequired[int]
  """Number of sub-users successfully unassigned from the fee group."""
  failedList: NotRequired[list[FeeGroupMemberFailure]]
  """Sub-users that could not be unassigned from the fee group."""


class UnassignFeeGroupMembersResponse(TypedDict):
  """Fee group member unassignment response frame. This product line wraps its business data in {code,message,data} on the wire, and the core does not strip it -- see spec/core.md's Envelope section."""

  code: NotRequired[str]
  """Response code. "000000" indicates success."""
  message: NotRequired[str]
  """Response message."""
  data: NotRequired[UnassignFeeGroupMembersResult]


class FeeGroupMembersUnassign(RpcEndpoint):
  """Remove sub-accounts from a commission fee group. Requires the API key's "trade" option to be enabled."""

  async def fee_group_members_unassign(
    self,
    *,
    group_code: str,
    sub_user_ids: list[int],
    validate: bool | None = None,
  ) -> UnassignFeeGroupMembersResponse:
    """Remove sub-accounts from a commission fee group. Requires the API key's "trade" option to be enabled.

    Args:
      group_code: Fee group code.
      sub_user_ids: Sub-user IDs to unassign from the fee group.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-vip-caas/api/rest-api/fee-groups#unassign-members-from-fee-group)
    """
    params: dict = {
      'groupCode': group_code,
      'subUserIds': dumps(sub_user_ids, separators=(',', ':')),
    }
    _Response = UnassignFeeGroupMembersResponse
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/sapi/v1/vip/caas/commission/fee-groups/members',
      params=params,
      validator=_validator,
      validate=validate,
    )
