"""Cosmos bank denom metadata query-string query."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
from dydx.protos.cosmos.bank import v1beta1 as bank_proto

class DenomMetadataByQueryString(GrpcEndpoint):
  """Bank denom metadata by query string endpoint."""

  @wrap_exceptions
  async def denom_metadata_by_query_string(
    self, denom: str,
  ) -> bank_proto.QueryDenomMetadataByQueryStringResponse:
    """Query metadata for one denom through the alternate query-string RPC.

    Args:
      denom: Base or display denomination to query.

    Returns:
      Metadata describing the denom display units and exponent.
    """
    request = bank_proto.QueryDenomMetadataByQueryStringRequest(denom=denom)
    return await bank_proto.QueryStub(self.channel).denom_metadata_by_query_string(request)
