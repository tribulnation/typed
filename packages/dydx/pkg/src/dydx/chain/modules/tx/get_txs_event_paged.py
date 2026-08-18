"""Cosmos tx event search pagination.

Hand-written: `get_txs_event`'s real, live-verified pagination is `page` strategy (flat
`page`/`limit`; the venue silently ignores the nested `pagination` request field despite
the message declaring one, and raises rather than returning a short/empty page once
`page` runs past the end -- see `spec/endpoints/chain/tx/get_txs_event/endpoint.json`'s
`notes`), which `codegen/python.py`'s `paged_response_method` hook does not cover yet
(`token` strategy with `absent_cursor` termination only). Kept in its own file, separate
from the codegen-owned `get_txs_event.py`, so re-running codegen doesn't overwrite it.
"""

from typed_core import PaginatedResponse

from dydx.chain.modules.tx.get_txs_event import GetTxsEvent
from dydx.protos.cosmos.base.abci import v1beta1 as abci_proto
from dydx.protos.cosmos.tx.v1beta1 import OrderBy

class GetTxsEventPaged(GetTxsEvent):
  """Transaction event search pagination."""

  def get_txs_event_paged(
    self,
    query: str | None = None, *,
    events: list[str] | None = None,
    order_by: OrderBy | None = None,
    limit: int,
  ) -> PaginatedResponse[abci_proto.TxResponse, int]:
    """Page through transactions matching event filters.

    Args:
      query: Optional event query expression.
      events: Optional event filters for legacy query semantics.
      order_by: Optional result ordering.
      limit: Rows per page. Required, unlike other `_paged` methods' optional `limit` --
        the walk is page-numbered rather than cursor-driven, so knowing when it's done
        means comparing a fixed, known page size against the response's own `total`
        rather than reading a next-cursor field back out of the response.

    Returns:
      A paginated response yielding transaction response pages.
    """
    async def next(page: int) -> tuple[list[abci_proto.TxResponse], int | None]:
      """Fetch the next transaction event page."""
      response = await self.get_txs_event(
        events or [],
        order_by=order_by if order_by is not None else OrderBy.UNSPECIFIED,
        page=page, limit=limit,
        query=query if query is not None else '',
      )
      rows = response.tx_responses
      collected = (page - 1) * limit + len(rows)
      return rows, (page + 1 if collected < response.total else None)

    return PaginatedResponse(1, next)
