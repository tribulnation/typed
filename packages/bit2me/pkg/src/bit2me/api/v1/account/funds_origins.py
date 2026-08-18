from typing_extensions import NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class FundsOriginTranslation(TypedDict):
  id: NotRequired[str]
  """Unique identifier of this fund origin."""
  name: NotRequired[str]
  """Machine-readable fund origin value, e.g. `salary` or `investments`."""
  description: NotRequired[str]
  """Human-readable label for this fund origin, in `langCode`'s language."""
  langCode: NotRequired[str]
  """ISO 639-1 language code of this translation, e.g. `en`."""


class ListFundsOriginsResponse(TypedDict):
  total: NotRequired[int]
  """Total number of fund origin translations returned."""
  data: NotRequired[list[FundsOriginTranslation]]
  """Fund origin translations, one entry per fund origin value."""


validate_response = validator(ListFundsOriginsResponse)


class FundsOrigins(RpcEndpoint):
  async def __call__(
    self,
    *,
    lang_code: str | None = None,
    validate: bool | None = None,
  ) -> ListFundsOriginsResponse:
    """Return all fund origins. Values are lowercase.

    Args:
      lang_code: Lang code
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/GET/v1/account/funds-origin)
    """
    params = {'langCode': lang_code} if lang_code is not None else None
    return await self.authed_request(
      'GET',
      '/v1/account/funds-origin',
      params=params,
      validator=validate_response,
      validate=validate,
    )
