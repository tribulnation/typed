from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Entry(TypedDict):
  iso: str
  """ISO 3166-2 region code."""
  iso3: NotRequired[str]
  """ISO 3166-2 alpha-3 region code."""
  name: str
  """Region name, localized per `langCode`."""
  fips: str
  """Federal Information Processing Standard  (https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards)"""


validate_response = validator(list[Entry])


class Countries(RpcEndpoint):
  async def countries(
    self,
    country_isocode: str,
    *,
    lang_code: Literal['EN', 'ES'] | None = None,
    validate: bool | None = None,
  ) -> list[Entry]:
    """Get country regions

    Args:
      country_isocode: ISO 3166-1 alpha-2 code of the country to list regions for.
      lang_code: Language fo localize country names
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/misc/GET/v1/misc/country/{countryISOCode}/region)
    """
    params = {'langCode': lang_code} if lang_code is not None else None
    return await self.authed_request(
      'GET',
      f'/v1/misc/country/{country_isocode}/region',
      params=params,
      validator=validate_response,
      validate=validate,
    )
