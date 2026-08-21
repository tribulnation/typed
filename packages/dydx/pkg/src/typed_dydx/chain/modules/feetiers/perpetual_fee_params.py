"""PerpetualFeeParams -- Query the perpetual fee tier parameters."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.feetiers as feetiers_proto


class PerpetualFeeParams(GrpcEndpoint):
  """Query the perpetual fee tier parameters."""

  @wrap_exceptions
  async def perpetual_fee_params(
    self,
  ) -> feetiers_proto.QueryPerpetualFeeParamsResponse:
    """Query the perpetual fee tier parameters."""
    return await feetiers_proto.QueryStub(self.channel).perpetual_fee_params(
      feetiers_proto.QueryPerpetualFeeParamsRequest()
    )
