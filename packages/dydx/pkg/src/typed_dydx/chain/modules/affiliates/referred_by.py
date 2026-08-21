"""ReferredBy -- Query the affiliate that referred an address."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.affiliates as affiliates_proto


class ReferredBy(GrpcEndpoint):
  """Query the affiliate that referred an address."""

  @wrap_exceptions
  async def referred_by(self, address: str) -> affiliates_proto.ReferredByResponse:
    """Query the affiliate that referred an address."""
    return await affiliates_proto.QueryStub(self.channel).referred_by(
      affiliates_proto.ReferredByRequest(address=address)
    )
