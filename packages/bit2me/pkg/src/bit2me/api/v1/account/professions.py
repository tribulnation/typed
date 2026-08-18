from typing_extensions import TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class ProfessionTranslation(TypedDict):
  id: str
  """Unique identifier of this profession category."""
  description: str
  """Human-readable label for this profession category, in `langCode`'s language."""
  professionCode: str
  """Numeric code identifying this profession category, e.g. `1`."""
  langCode: str
  """ISO 639-1 language code of this translation, e.g. `en`."""


class ListProfessionsResponse(TypedDict):
  total: int
  """Total number of profession translations returned."""
  data: list[ProfessionTranslation]
  """Profession translations, one entry per profession category."""


validate_response = validator(ListProfessionsResponse)


class Professions(RpcEndpoint):
  async def __call__(
    self,
    *,
    lang_code: str | None = None,
    validate: bool | None = None,
  ) -> ListProfessionsResponse:
    """Return all professions. Values are lowercase.

    Args:
      lang_code: Lang code
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/GET/v1/account/professions)
    """
    params = {'langCode': lang_code} if lang_code is not None else None
    return await self.authed_request(
      'GET',
      '/v1/account/professions',
      params=params,
      validator=validate_response,
      validate=validate,
    )
