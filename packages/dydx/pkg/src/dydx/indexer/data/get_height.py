"""dYdX indexer get height types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from typing_extensions import TypedDict
from .core import IndexerMixin, response_parser

class HeightResponse(TypedDict):
  """Height response payload."""
  height: str
  time: datetime

parse_response = response_parser(HeightResponse)

@dataclass
class GetHeight(IndexerMixin):
  """Endpoint mixin for height."""
  async def get_height(
    self,
    validate: bool | None = None
  ) -> HeightResponse:
    """Fetch the latest indexer block height.
  
    Args:
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/utility#get-height)
    """
    r = await self.request('GET', '/v4/height')
    return parse_response(r, validate=self.validate(validate))

