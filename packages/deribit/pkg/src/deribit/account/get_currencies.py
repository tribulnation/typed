"""`private/get_currencies` — `private/get_currencies`."""

from typing_extensions import TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class AccountCurrency(TypedDict):
  currency: str
  """Currency code, lower- or upper-case as the venue returns it (observed live in upper-case, e.g. `"BTC"`)."""


validate_get_currencies = validator[list[AccountCurrency]](list[AccountCurrency])


class GetCurrencies(RpcEndpoint):
  """`private/get_currencies`."""

  async def get_currencies(
    self, *, validate: bool | None = None
  ) -> list[AccountCurrency]:
    """Returns a list of cryptocurrencies available for the authenticated user's account. This is the account-scoped counterpart of `public/get_currencies` (`market_data.get_currencies`): the public method lists every currency the platform supports, this one lists only the currencies enabled on the caller's own account. Takes no parameters.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-get_currencies)
    """
    return await self.authed_request(
      'private/get_currencies', validator=validate_get_currencies, validate=validate
    )
