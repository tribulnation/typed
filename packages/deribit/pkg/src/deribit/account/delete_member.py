"""`private/delete_member` — `private/delete_member`."""

from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Member(TypedDict):
  """A Direct Access member: an external identity (e.g. a FIX or Direct Access order gateway user) that can be granted Direct Access trading rights on the account or one of its subaccounts."""

  member_id: NotRequired[int]
  """Member identifier. Present when the request is made from the main account."""
  main_uid: NotRequired[int]
  """User id of the main account the member belongs to. Present when the request is made from the main account."""
  name: str
  """Name of the member."""
  is_active: bool
  """Whether the member is active. Only active members have Direct Access trading rights."""
  accounts: NotRequired[list[int]]
  """(Sub)account user ids the member has Direct Access trading rights on. Present when the request is made from the main account."""
  m_tstamp: NotRequired[int]
  """Timestamp of the member's last modification, milliseconds since the Unix epoch. Present when the request is made from the main account."""


class MembersList(TypedDict):
  members: list[Member]
  """All Direct Access members configured for the account, after the deletion."""
  is_direct_access_allowed: bool
  """Whether Direct Access trading is enabled for the account."""


validate_delete_member = validator[MembersList](MembersList)


class DeleteMember(RpcEndpoint):
  """`private/delete_member`."""

  async def delete_member(
    self,
    *,
    member_id: int,
    validate: bool | None = None,
  ) -> MembersList:
    """Deletes a Direct Access member from the account and returns the resulting list of all members configured for the account. Dedicated to Starbase; requires Direct Access trading to be enabled for the account.

    Args:
      member_id: Id of the member to delete.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-delete_member)
    """
    params: dict = {
      'member_id': member_id,
    }
    return await self.authed_request(
      'private/delete_member',
      params=params,
      validator=validate_delete_member,
      validate=validate,
    )
