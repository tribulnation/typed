"""`private/get_new_announcements` — `private/get_new_announcements`."""

from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Announcement(TypedDict):
  id: float
  """A unique identifier for the announcement."""
  title: str
  """The title of the announcement."""
  body: str
  """The HTML body of the announcement."""
  important: bool
  """Whether the announcement is marked as important."""
  confirmation: NotRequired[bool]
  """Whether the user confirmation is required for this announcement."""
  publication_timestamp: int
  """The timestamp (milliseconds since the Unix epoch) of announcement publication."""


validate_get_new_announcements = validator[list[Announcement]](list[Announcement])


class GetNewAnnouncements(RpcEndpoint):
  """`private/get_new_announcements`."""

  async def get_new_announcements(
    self,
    *,
    validate: bool | None = None,
  ) -> list[Announcement]:
    """Retrieves only unread announcements for the authenticated account. Announcements are marked as read via `set_announcement_as_read` or by viewing them through the web interface. Takes no parameters.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-get_new_announcements)
    """
    return await self.authed_request(
      'private/get_new_announcements',
      validator=validate_get_new_announcements,
      validate=validate,
    )
