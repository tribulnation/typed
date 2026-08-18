from typing_extensions import NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class EmploymentStatusTranslation(TypedDict):
  id: NotRequired[str]
  """Unique identifier of this employment status."""
  name: NotRequired[str]
  """Machine-readable employment status value, e.g. `employed` or `selfEmployed`."""
  description: NotRequired[str]
  """Human-readable label for this employment status, in `langCode`'s language."""
  langCode: NotRequired[str]
  """ISO 639-1 language code of this translation, e.g. `en`."""


class ListEmploymentStatusesResponse(TypedDict):
  total: NotRequired[int]
  """Total number of employment status translations returned."""
  data: NotRequired[list[EmploymentStatusTranslation]]
  """Employment status translations, one entry per employment status value."""


validate_response = validator(ListEmploymentStatusesResponse)


class EmploymentStatuses(RpcEndpoint):
  async def __call__(
    self,
    *,
    lang_code: str | None = None,
    validate: bool | None = None,
  ) -> ListEmploymentStatusesResponse:
    """Return all employment status translations. Values are lowercase.

    Args:
      lang_code: Lang code
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/GET/v1/account/employment-status)
    """
    params = {'langCode': lang_code} if lang_code is not None else None
    return await self.authed_request(
      'GET',
      '/v1/account/employment-status',
      params=params,
      validator=validate_response,
      validate=validate,
    )
