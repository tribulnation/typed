"""dYdX indexer get screen types and endpoint."""

from dataclasses import dataclass
from typing_extensions import TypedDict
from .core import IndexerMixin, response_parser

class ComplianceResponse(TypedDict):
  """Compliance response payload."""
  restricted: bool
  reason: str

parse_response = response_parser(ComplianceResponse)

@dataclass
class GetScreen(IndexerMixin):
  """Endpoint mixin for screen."""
  async def get_screen(
    self,
    address: str,
    *,
    validate: bool | None = None
  ) -> ComplianceResponse:
    """Get screen.
  
    Args:
      address: Wallet address to screen.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/utility#get-screen)
    """
    params: dict[str, object] = {
      'address': address,
    }
    r = await self.request('GET', '/v4/screen', params=params)
    return parse_response(r, validate=self.validate(validate))
