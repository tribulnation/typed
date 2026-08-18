from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class RedemptionForecastEntry(TypedDict):
  """One portfolio's redemption forecast for one date."""

  portfolioId: NotRequired[str]
  """CC portfolio ID."""
  portfolioName: NotRequired[str]
  """Portfolio name."""
  currency: NotRequired[str]
  """Portfolio currency."""
  forecastDate: NotRequired[int]
  """Forecast date, as a millisecond epoch timestamp."""
  units: NotRequired[str]
  """Total units pending redemption."""
  navPerUnit: NotRequired[str | None]
  """NAV per unit (T-1). Null when not yet available."""
  estimatedAmount: NotRequired[str | None]
  """Estimated redemption amount, `units * navPerUnit`. Null when `navPerUnit` is not yet available."""


class RedemptionCalendar(TypedDict):
  """The IM's redemption forecast for the next 8 days."""

  items: NotRequired[list[RedemptionForecastEntry]]
  """Per-portfolio, per-date redemption forecast entries."""


class RedemptionCalendarEndpoint(RpcEndpoint):
  """Query the upcoming redemption forecast for the next 8 days across all portfolios managed by the institutional manager. Takes no business parameters -- IM identity is resolved from the API key."""

  async def redemption_calendar(
    self,
    *,
    validate: bool | None = None,
  ) -> RedemptionCalendar:
    """Query the upcoming redemption forecast for the next 8 days across all portfolios managed by the institutional manager. Takes no business parameters -- IM identity is resolved from the API key.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-fund-account/api/rest-api/~#redemption-calendar)
    """
    _Response = RedemptionCalendar
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/capital-connect/redemption/calendar',
      validator=_validator,
      validate=validate,
    )
