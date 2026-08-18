"""`private/get_access_log` — `private/get_access_log`."""

from typing_extensions import Any, AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class AccessLogEntry(TypedDict):
  id: int
  """Unique identifier."""
  ip: str
  """IP address of the source that generated the event."""
  timestamp: int
  """The timestamp (milliseconds since the Unix epoch)."""
  country: str
  """Estimated country where the IP address is registered."""
  city: str
  """Estimated city where the IP address is registered."""
  log: str
  """Action description. Documented values include: `changed_email`, `changed_password`, `disabled_tfa`, `enabled_tfa`, `success` (login), `failure` (login), `enabled_subaccount_login`, `disabled_subaccount_login`, `new_api_key`, `removed_api_key`, `changed_scope`, `changed_whitelist`, `disabled_api_key`, `enabled_api_key`, `reset_api_key`. Not declared `enum`: the live account also produced `security_key_authorization`, which is not in this documented list, so the set is evidently not closed."""
  name: NotRequired[str]
  """Name associated with the event (e.g. the Security Key's registered name). Not in the venue's own documented schema for this field, observed live on `security_key_authorization` entries."""
  method: NotRequired[str]
  """JSON-RPC method the event relates to, e.g. `"private/create_api_key"`. Not in the venue's own documented schema for this field, observed live."""
  identity_provider: NotRequired[str]
  """Identity provider for the event, e.g. `"deribit"`. Not in the venue's own documented schema for this field, observed live."""
  key_type: NotRequired[str]
  """Security key type, e.g. `"u2f"`. Not in the venue's own documented schema for this field, observed live."""
  assignment: NotRequired[str]
  """Security key assignment the event applies to, e.g. `"account"`. Not in the venue's own documented schema for this field, observed live."""
  data: NotRequired[dict[str, Any] | str]
  """Additional information about the action; shape depends on `log`'s value (e.g. a subaccount uid, or an API key's `client_id`)."""


class GetAccessLogResult(TypedDict):
  records_total: int
  """Total number of access log entries available for this account."""
  data: list[AccessLogEntry]
  """Access log entries for this page, newest first."""


validate_get_access_log = validator[GetAccessLogResult](GetAccessLogResult)


class GetAccessLog(RpcEndpoint):
  """`private/get_access_log`."""

  async def get_access_log(
    self,
    *,
    offset: int | None = None,
    count: int | None = None,
    validate: bool | None = None,
  ) -> GetAccessLogResult:
    """Retrieves a log of API access attempts and account security/authentication events for the authenticated account (IP address, location, event type, timestamp). Useful for monitoring account security and reviewing usage patterns. Paginated via `offset`/`count`.

    Args:
      offset: The offset for pagination, default 0.
      count: Number of requested items, default 10, maximum 1000.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-get_access_log)
    """
    params = {}
    if offset is not None:
      params['offset'] = offset
    if count is not None:
      params['count'] = count
    return await self.authed_request(
      'private/get_access_log',
      params=params,
      validator=validate_get_access_log,
      validate=validate,
    )

  async def get_access_log_paged(
    self,
    *,
    count: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[GetAccessLogResult]:
    """Yield successive pages of `get_access_log`.

    Advances `offset` by `(count if count is not None else 10)` and stops once it has
    covered the `records_total` items the response reports, or after `max_pages` pages
    when one is given.
    """
    offset = 0
    pages = 0
    while True:
      response = await self.get_access_log(
        count=count, offset=offset, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('records_total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or count is None or pages * count >= total:
        break
      offset += count if count is not None else 10
