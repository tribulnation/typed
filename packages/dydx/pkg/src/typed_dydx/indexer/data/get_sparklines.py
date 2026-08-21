"""dYdX indexer get sparklines types and endpoint."""

from dataclasses import dataclass
from decimal import Decimal
from typing_extensions import Literal
from .core import IndexerMixin, response_parser

Sparkline = dict[str, list[Decimal]]

parse_response = response_parser(Sparkline)

@dataclass
class GetSparklines(IndexerMixin):
  """Endpoint mixin for sparklines."""
  async def get_sparklines(
    self,
    *,
    time_period: Literal['OneDay', 'SevenDays'],
    validate: bool | None = None
  ) -> Sparkline:
    """Get sparklines.
  
    Args:
      time_period: Sparkline time period.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/markets#get-sparklines)
    """
    params: dict[str, object] = {
      'timePeriod': time_period,
    }
    r = await self.request('GET', '/v4/sparklines', params=params)
    return parse_response(r, validate=self.validate(validate))

