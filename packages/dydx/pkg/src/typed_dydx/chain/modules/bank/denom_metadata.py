"""Cosmos bank denom metadata query."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
from typed_dydx.protos.cosmos.bank import v1beta1 as bank_proto

class DenomMetadata(GrpcEndpoint):
  """Bank denom metadata endpoint."""

  @wrap_exceptions
  async def denom_metadata(self, denom: str) -> bank_proto.QueryDenomMetadataResponse:
    """Query metadata for one denom.

    Args:
      denom: Base or display denomination to query.

    Returns:
      Metadata describing the denom display units and exponent.
    """
    request = bank_proto.QueryDenomMetadataRequest(denom=denom)
    return await bank_proto.QueryStub(self.channel).denom_metadata(request)
