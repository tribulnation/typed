"""`private/set_member` — `private/set_member`."""

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
  """All Direct Access members configured for the account, after the create/edit."""
  is_direct_access_allowed: bool
  """Whether Direct Access trading is enabled for the account."""


validate_set_member = validator[MembersList](MembersList)


class SetMember(RpcEndpoint):
  """`private/set_member`."""

  async def set_member(
    self,
    *,
    member_id: int | None = None,
    name: str,
    is_active: bool | None = None,
    accounts: list[int] | None = None,
    validate: bool | None = None,
  ) -> MembersList:
    """Creates a new Direct Access member, or edits an existing one, and returns the resulting list of all members configured for the account. Omit `member_id` to create a new member -- a non-empty `accounts` list is then required, and the member cannot be created inactive. Pass an existing `member_id` to edit that member's `name` or `accounts`, or to toggle its `is_active` state; toggling `is_active` and changing `name`/`accounts` cannot be done in the same request. Dedicated to Starbase; requires Direct Access trading to be enabled for the account.

    Args:
      member_id: Id of the member to edit. Omit to create a new member.
      name: Name of the member.
      is_active: Whether the member should be active. A member cannot be created inactive.
      accounts: (Sub)account user ids to grant the member Direct Access trading rights on.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-set_member)
    """
    params: dict = {
      'name': name,
    }
    if member_id is not None:
      params['member_id'] = member_id
    if is_active is not None:
      params['is_active'] = is_active
    if accounts is not None:
      params['accounts'] = accounts
    return await self.authed_request(
      'private/set_member',
      params=params,
      validator=validate_set_member,
      validate=validate,
    )
