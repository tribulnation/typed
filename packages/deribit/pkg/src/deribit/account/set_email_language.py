"""`private/set_email_language` — `private/set_email_language`."""

from typing_extensions import Literal
from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_set_email_language = validator[Literal['ok']](Literal['ok'])  # pyright: ignore[reportArgumentType]  # fmt: skip


class SetEmailLanguage(RpcEndpoint):
  """`private/set_email_language`."""

  async def set_email_language(
    self,
    *,
    language: str,
    validate: bool | None = None,
  ) -> Literal['ok']:
    """Sets the preferred language for email notifications sent to the account. Only affects future email notifications, not the web interface or API responses. Not gated behind two-factor authentication -- confirmed live.

    Args:
      language: Abbreviated language name. The venue documents example values only (`en`, `ko`, `zh`, `ja`, `ru`) in prose, not a closed set -- left un-enum'd, matching `account.get_email_language`'s own read-half spec of the identical field.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-set_email_language)
    """
    params: dict = {
      'language': language,
    }
    return await self.authed_request(
      'private/set_email_language',
      params=params,
      validator=validate_set_email_language,
      validate=validate,
    )
