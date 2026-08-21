"""CollateralPoolAddress -- Query the collateral pool account address for a perpetual id."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.subaccounts as subaccounts_proto


class CollateralPoolAddress(GrpcEndpoint):
  """Query the collateral pool account address for a perpetual id."""

  @wrap_exceptions
  async def collateral_pool_address(
    self,
    perpetual_id: int,
  ) -> subaccounts_proto.QueryCollateralPoolAddressResponse:
    """Query the collateral pool account address for a perpetual id."""
    return await subaccounts_proto.QueryStub(self.channel).collateral_pool_address(
      subaccounts_proto.QueryCollateralPoolAddressRequest(perpetual_id=perpetual_id)
    )
