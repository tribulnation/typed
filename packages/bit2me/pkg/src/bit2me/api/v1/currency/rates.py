from typing_extensions import Literal, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Entry(TypedDict):
  fiat: dict[str, float]
  """Exchange rate (in USD) for each supported fiat currency, keyed by ISO 4217 code."""
  crypto: dict[str, float]
  """Exchange rate (in USD) for each supported crypto asset, keyed by asset symbol."""


validate_response = validator(list[Entry])


class Rates(RpcEndpoint):
  async def rates(
    self,
    *,
    type: Literal['all', 'fiat', 'crypto'] | None = None,
    time: str,
    validate: bool | None = None,
  ) -> list[Entry]:
    """Return all supported exchange rates in USD.

    Args:
      type: Currency type
      time: Comma delimited list of times (ISO 8601 or epoch). If this parameter is not specifed, the current time is used
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/market/GET/v1/currency/rate)
    """
    params: dict = {
      'time': time,
    }
    if type is not None:
      params['type'] = type
    return await self.authed_request(
      'GET',
      '/v1/currency/rate',
      params=params,
      validator=validate_response,
      validate=validate,
    )
