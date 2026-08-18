from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Point(TypedDict):
  time: int
  """Time this price point was recorded, in Unix epoch milliseconds."""
  interval: NotRequired[
    Literal['one_hour', 'one_day', 'one_week', 'one_month', 'one_year']
  ]
  """Interval this price point represents. Absent for the current-rate point."""
  price: str
  """Asset price at `time`, in `currency`."""


validate_response = validator(dict[str, list[Point]])


class Prices(RpcEndpoint):
  async def prices(
    self,
    *,
    currency: str | None = None,
    interval: list[Literal['one_hour', 'one_day', 'one_week', 'one_month', 'one_year']]
    | None = None,
    validate: bool | None = None,
  ) -> dict[str, list[Point]]:
    """Return cryptocurrency prices in the selected currency across the requested intervals, including the current rate.

    Args:
      currency: Fiat or crypto currency to price against. Defaults to the account's base currency when omitted.
      interval: Period of time for consultation
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/market/GET/v1/currency/prices)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    if interval is not None:
      params['interval'] = interval
    return await self.authed_request(
      'GET',
      '/v1/currency/prices',
      params=params,
      validator=validate_response,
      validate=validate,
    )
