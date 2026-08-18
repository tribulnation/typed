"""Asset -- Query an asset by id."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.assets as assets_proto


class Asset(GrpcEndpoint):
  """Query an asset by id."""

  @wrap_exceptions
  async def asset(self, id: int) -> assets_proto.QueryAssetResponse:
    """Query an asset by id."""
    return await assets_proto.QueryStub(self.channel).asset(
      assets_proto.QueryAssetRequest(id=id)
    )
