"""`user.access_log` — subscription."""

from typing_extensions import Any, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class AccessLogUpdate(TypedDict):
  """Message schema for `user.access_log` subscription - contains the data payload"""

  id: int
  """Unique identifier"""
  ip: str
  """IP address of source that generated action"""
  timestamp: int
  """The timestamp (milliseconds since the Unix epoch)"""
  country: str
  """Country where the IP address is registered (estimated)"""
  city: str
  """City where the IP address is registered (estimated)"""
  log: str
  """Action description. Possible values:

- ``changed_email`` - email was changed
- ``changed_password`` - password was changed
- ``disabled_tfa`` - TFA was disabled
- ``enabled_tfa`` - TFA was enabled
- ``success`` - successful login
- ``failure`` - login failure
- ``enabled_subaccount_login`` - login was enabled for subaccount (in `data` - subaccount uid)
- ``disabled_subaccount_login`` - login was disabled for subaccount (in `data` - subaccount uid)
- ``new_api_key`` - API key was created (in `data` key client id)
- ``removed_api_key`` - API key was removed (in `data` key client id)
- ``changed_scope`` - scope of API key was changed (in `data` key client id)
- ``changed_whitelist`` - whitelist of API key was edited (in `data` key client id)
- ``disabled_api_key`` - API key was disabled (in `data` key client id)
- ``enabled_api_key`` - API key was enabled (in `data` key client id)
- ``reset_api_key`` - API key was reset (in `data` key client id)"""
  data: NotRequired[dict[str, Any] | str]
  """Optional, additional information about action, type depends on `log` value"""


validate_access_log = validator[AccessLogUpdate](AccessLogUpdate)


class AccessLog(StreamEndpoint):
  """`user.access_log` subscription."""

  def access_log(
    self,
    *,
    validate: bool | None = None,
  ) -> StreamManager[AccessLogUpdate, Any, Any]:
    """Security event notifications for the account.

    Use this channel to monitor account-related security events (e.g., access log entries) and build alerting around suspicious activity.

    Args:
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/subscriptions/user-access_log)
    """
    channel = f'user.access_log'
    return self.authed_subscribe(
      channel, validator=validate_access_log, validate=validate
    )
