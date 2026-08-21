"""dYdX indexer get time types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from typing_extensions import TypedDict
from .core import IndexerMixin, response_parser

class TimeResponse(TypedDict):
  """Time response payload."""
  iso: datetime
  epoc: float

parse_response = response_parser(TimeResponse)

@dataclass
class GetTime(IndexerMixin):
  """Endpoint mixin for time."""
  async def get_time(
    self,
    validate: bool | None = None
  ) -> TimeResponse:
    """Fetch the indexer server time.
  
    Args:
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/utility#get-time)
    """
    r = await self.request('GET', '/v4/time')
    return parse_response(r, validate=self.validate(validate))

