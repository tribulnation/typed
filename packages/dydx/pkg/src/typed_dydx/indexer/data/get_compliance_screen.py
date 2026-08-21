"""dYdX indexer get compliance screen types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from typing_extensions import Literal, NotRequired, TypedDict
from .core import IndexerMixin, response_parser

class ComplianceV2Response(TypedDict):
  """Compliance v2 response payload."""
  status: Literal['COMPLIANT', 'FIRST_STRIKE_CLOSE_ONLY', 'FIRST_STRIKE', 'CLOSE_ONLY', 'BLOCKED']
  reason: NotRequired[Literal['MANUAL', 'US_GEO', 'CA_GEO', 'GB_GEO', 'SANCTIONED_GEO', 'COMPLIANCE_PROVIDER'] | None]
  updatedAt: NotRequired[datetime | None]

parse_response = response_parser(ComplianceV2Response)

@dataclass
class GetComplianceScreen(IndexerMixin):
  """Endpoint mixin for compliance_screen."""
  async def get_compliance_screen(
    self,
    address: str,
    validate: bool | None = None
  ) -> ComplianceV2Response:
    """Get compliance screen.
  
    Args:
      address: EVM or dYdX address.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/utility#get-compliance-screen)
    """
    r = await self.request('GET', f'/v4/compliance/screen/{address}')
    return parse_response(r, validate=self.validate(validate))
