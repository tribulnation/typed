"""`public/get_apr_history` — `public/get_apr_history`."""

from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class AprDay(TypedDict):
  """The APR for one epoch day."""

  day: NotRequired[int]
  """The full epoch day"""
  apr: NotRequired[float]
  """The APR of the day"""


class AprHistory(TypedDict):
  """A page of APR history."""

  continuation: NotRequired[int]
  """Token for the next page, passed back as `before` -- absent once history is exhausted. Observed live as an integer epoch day (matching `before`'s own type), though the OpenAPI schema documents it as a string; the integer shape from `examples/02` is used here per rule 5."""
  data: list[AprDay]
  """APR values for this page, most recent day first."""


validate_get_apr_history = validator[AprHistory](AprHistory)


class GetAprHistory(RpcEndpoint):
  """`public/get_apr_history`."""

  async def get_apr_history(
    self,
    *,
    currency: Literal['usde', 'steth', 'usdc', 'build'],
    limit: int | None = None,
    before: int | None = None,
    validate: bool | None = None,
  ) -> AprHistory:
    """Retrieves historical Annual Percentage Rate (APR) data for yield-generating tokens. APR represents the annualized return rate for holding these tokens on Deribit.

    This method is only applicable to yield-generating tokens: `USDE`, `STETH`, `USDC`, and `BUILD`. Use the `limit` parameter to specify the number of days to retrieve (default 365, maximum 365), and `before` to retrieve APR history before a specific epoch day.

    **📖 Related Support Article:** [Yield reward-bearing coins](https://support.deribit.com/hc/en-us/articles/31424939199261-Yield-reward-bearing-coins)

    Args:
      currency: Currency for which to retrieve APR history
      limit: Number of days to retrieve (default `365`, maximum `365`)
      before: Used to receive APR history before given epoch day
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_apr_history)
    """
    params: dict = {
      'currency': currency,
    }
    if limit is not None:
      params['limit'] = limit
    if before is not None:
      params['before'] = before
    return await self.request(
      'public/get_apr_history',
      params=params,
      validator=validate_get_apr_history,
      validate=validate,
    )

  async def get_apr_history_paged(
    self,
    *,
    currency: Literal['usde', 'steth', 'usdc', 'build'],
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[AprHistory]:
    """Yield successive pages of `get_apr_history`.

    Passes each page's token back as `before` and stops when a response carries no
    `continuation`, or after `max_pages` pages when one is given.
    """
    before: int | None = None
    pages = 0
    while True:
      response = await self.get_apr_history(
        currency=currency, limit=limit, before=before, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      before = response.get('continuation') if response is not None else None
      if not before:
        break
