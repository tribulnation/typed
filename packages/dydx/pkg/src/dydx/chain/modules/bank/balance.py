"""Balance -- Query one denom balance for an account address."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.cosmos.bank.v1beta1 as v1beta1_proto


class Balance(GrpcEndpoint):
  """Query one denom balance for an account address."""

  @wrap_exceptions
  async def balance(
    self, *, address: str, denom: str
  ) -> v1beta1_proto.QueryBalanceResponse:
    """Query one denom balance for an account address."""
    return await v1beta1_proto.QueryStub(self.channel).balance(
      v1beta1_proto.QueryBalanceRequest(address=address, denom=denom)
    )
