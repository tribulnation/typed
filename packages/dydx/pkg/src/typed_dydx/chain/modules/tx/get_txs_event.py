"""GetTxsEvent -- Query transactions matching a CometBFT event query expression."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.tx.v1beta1 as v1beta1_proto
from typed_dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from typed_dydx.protos.cosmos.tx.v1beta1 import OrderBy


class GetTxsEvent(GrpcEndpoint):
  """Query transactions matching a CometBFT event query expression."""

  @wrap_exceptions
  async def get_txs_event(
    self,
    events: list[str],
    *,
    pagination: PageRequest | None = None,
    order_by: OrderBy,
    page: int,
    limit: int,
    query: str,
  ) -> v1beta1_proto.GetTxsEventResponse:
    """Query transactions matching a CometBFT event query expression."""
    return await v1beta1_proto.ServiceStub(self.channel).get_txs_event(
      v1beta1_proto.GetTxsEventRequest(
        events=events,
        pagination=pagination,
        order_by=order_by,
        page=page,
        limit=limit,
        query=query,
      )
    )
