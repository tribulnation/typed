"""`announcements` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class Announcement(TypedDict):
  """General platform announcement (maintenance notice, incident, or update)."""

  id: int
  """Announcement's identifier."""
  title: str
  """Announcement's title."""
  body: str
  """HTML-formatted announcement body."""
  publication_timestamp: int
  """The timestamp (milliseconds since the Unix epoch) of announcement publication."""
  important: bool
  """Whether the announcement is marked as important."""
  confirmation: NotRequired[bool]
  """Whether user confirmation is required for this announcement."""
  unread: NotRequired[int]
  """The number of previous unread announcements. Only present for authorized users."""
  action: Literal['new', 'deleted']
  """Action taken by the platform administrators: published a `new` announcement, or `deleted` an old one."""


validate_announcements = validator[Announcement](Announcement)


class Announcements(StreamEndpoint):
  """`announcements` subscription."""

  def announcements(
    self,
    *,
    validate: bool | None = None,
  ) -> StreamManager[Announcement, Any, Any]:
    """General announcements concerning the Deribit platform. Subscribe to receive operational messages such as maintenance notices, incidents, and important platform updates.

    Args:
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/announcements/announcements)
    """
    channel = f'announcements'
    return self.subscribe(channel, validator=validate_announcements, validate=validate)
