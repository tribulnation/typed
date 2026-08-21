"""Comet transaction search endpoint."""

import json

from pydantic import TypeAdapter
from typed_core import PaginatedResponse
from typing_extensions import Literal

from typed_dydx.chain.comet.core import CometEndpoint
from typed_dydx.chain.comet.types import TxResponse, TxSearchResponse


tx_search_adapter = TypeAdapter(TxSearchResponse)


class TxSearch(CometEndpoint):
  """Comet transaction search endpoint group."""

  async def tx_search(
    self,
    query: str,
    *,
    prove: bool | None = None,
    page: int | None = None,
    per_page: int | None = None,
    order_by: Literal['asc', 'desc'] | None = None,
    validate: bool | None = None,
  ) -> TxSearchResponse:
    """Search indexed Comet transactions by event query.

    Args:
      query: Comet event query expression.
      prove: Include proofs for returned transactions.
      page: Page number for paginated results.
      per_page: Maximum transactions to return on the page.
      order_by: Sort order for matching transactions.
      validate: Validation override for this request.

    Returns:
      Transaction search result.

    References:
      - [CometBFT RPC docs](https://docs.cosmos.network/cometbft/latest/api-reference/rpc/info/tx_search)
    """
    params: dict[str, str | bool | int] = {'query': json.dumps(query)}
    if prove is not None:
      params['prove'] = prove
    if page is not None:
      params['page'] = page
    if per_page is not None:
      params['per_page'] = per_page
    if order_by is not None:
      params['order_by'] = json.dumps(order_by)
    return await self.result('/tx_search', params=params, result_adapter=tx_search_adapter, validate=validate)

  def tx_search_paged(
    self,
    query: str,
    *,
    prove: bool | None = None,
    per_page: int | None = None,
    order_by: Literal['asc', 'desc'] | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[TxResponse, tuple[int, int]]:
    """Page through indexed Comet transactions by event query.

    Args:
      query: Comet event query expression.
      prove: Include proofs for returned transactions.
      per_page: Maximum transactions to return on each page.
      order_by: Sort order for matching transactions.
      validate: Validation override for each request.

    Returns:
      A paginated response yielding matching transaction pages.

    References:
      - [CometBFT RPC docs](https://docs.cosmos.network/cometbft/latest/api-reference/rpc/info/tx_search)
    """
    async def next(state: tuple[int, int]) -> tuple[list[TxResponse], tuple[int, int] | None]:
      """Fetch the next transaction search page."""
      page, seen = state
      response = await self.tx_search(
        query,
        prove=prove,
        page=page,
        per_page=per_page,
        order_by=order_by,
        validate=validate,
      )
      txs = response['txs']
      seen += len(txs)
      total = int(response['total_count'])
      if seen >= total or not txs:
        return txs, None
      return txs, (page + 1, seen)

    return PaginatedResponse((1, 0), next)
