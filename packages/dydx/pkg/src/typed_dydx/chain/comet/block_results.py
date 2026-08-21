"""Comet block results endpoint."""

from pydantic import TypeAdapter

from typed_dydx.chain.comet.core import CometEndpoint
from typed_dydx.chain.comet.types import BlockResultsResponse


block_results_adapter = TypeAdapter(BlockResultsResponse)


class BlockResults(CometEndpoint):
  """Comet block results endpoint group."""

  async def block_results(
    self,
    height: int | None = None,
    validate: bool | None = None,
  ) -> BlockResultsResponse:
    """Return ABCI execution results for a block.

    Args:
      height: Block height whose execution results should be returned.
      validate: Validation override for this request.

    Returns:
      Block execution results.

    References:
      - [CometBFT RPC docs](https://docs.cosmos.network/cometbft/latest/api-reference/rpc/info/block_results)
    """
    params = {'height': height} if height is not None else None
    return await self.result('/block_results', params=params, result_adapter=block_results_adapter, validate=validate)

