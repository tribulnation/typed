"""`GET /v5/market/risk-limit` — Get Risk Limit."""

from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from bybit.core import Endpoint, validator


class RiskLimitTier(TypedDict):
  """One risk limit tier."""

  id: int
  """Tier identifier."""
  symbol: str
  """Symbol name."""
  riskLimitValue: str
  """Position value ceiling of the tier."""
  maintenanceMargin: str
  """Maintenance margin rate of the tier."""
  initialMargin: str
  """Initial margin rate of the tier."""
  isLowestRisk: Literal[0, 1]
  """Whether this is the lowest tier: `1` for yes, `0` for no."""
  maxLeverage: str
  """Maximum leverage allowed in the tier."""
  mmDeduction: str
  """Maintenance margin deduction applied when entering the tier."""


class RiskLimitResult(TypedDict):
  """Risk limit tiers."""

  category: Literal['linear', 'inverse']
  """Product type."""
  list: list[RiskLimitTier]
  """Risk limit tiers, ordered from the lowest tier upwards."""
  nextPageCursor: NotRequired[str]
  """Opaque cursor for the next page. Pass it back as `cursor`; an empty string means there are no further pages."""


adapter = validator[RiskLimitResult](RiskLimitResult)


class RiskLimit(Endpoint):
  """`Get Risk Limit` — mixed into the router that owns `market.risk_limit`."""

  async def risk_limit(
    self,
    *,
    category: Literal['linear', 'inverse'],
    symbol: str | None = None,
    cursor: str | None = None,
    validate: bool | None = None,
  ) -> RiskLimitResult:
    """Get the risk limit tiers of a contract: position ceiling, margin rates and maximum leverage per tier.

    Args:
      category: Product type.
      symbol: Symbol name in uppercase, for example `BTCUSDT`. Omit to return every contract in the category.
      cursor: Opaque pagination cursor. Pass the `nextPageCursor` returned by the previous page; omit it for the first page.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/risk-limit)
    """
    params: dict = {
      'category': category,
    }
    if symbol is not None:
      params['symbol'] = symbol
    if cursor is not None:
      params['cursor'] = cursor
    r = await self.request('GET', '/v5/market/risk-limit', params=params)
    return self.result(r, adapter, validate)

  async def risk_limit_paged(
    self,
    *,
    category: Literal['linear', 'inverse'],
    symbol: str | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[RiskLimitResult]:
    """Yield successive pages of `risk_limit`.

    Passes each page's token back as `cursor` and stops when a response carries no
    `nextPageCursor`, or after `max_pages` pages when one is given.
    """
    cursor: str | None = None
    pages = 0
    while True:
      response = await self.risk_limit(
        category=category, symbol=symbol, cursor=cursor, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      cursor = response.get('nextPageCursor')
      if not cursor:
        break
