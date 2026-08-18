"""Subaccount -- Query a single subaccount by owner address and subaccount number."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.subaccounts as subaccounts_proto


class Subaccount(GrpcEndpoint):
  """Query a single subaccount by owner address and subaccount number."""

  @wrap_exceptions
  async def subaccount(
    self,
    owner: str,
    *,
    number: int,
  ) -> subaccounts_proto.QuerySubaccountResponse:
    """Query a single subaccount by owner address and subaccount number."""
    return await subaccounts_proto.QueryStub(self.channel).subaccount(
      subaccounts_proto.QueryGetSubaccountRequest(owner=owner, number=number)
    )
