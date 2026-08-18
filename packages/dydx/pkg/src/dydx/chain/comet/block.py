"""Comet block endpoint."""

from pydantic import TypeAdapter

from dydx.chain.comet.core import CometEndpoint
from dydx.chain.comet.types import BlockResponse


block_adapter = TypeAdapter(BlockResponse)


class Block(CometEndpoint):
  """Comet block endpoint group."""

  async def block(
    self,
    height: int | None = None,
    validate: bool | None = None,
  ) -> BlockResponse:
    """Return a Comet block by height or the latest block.

    Args:
      height: Block height to fetch.
      validate: Validation override for this request.

    Returns:
      Block result.

    References:
      - [CometBFT RPC docs](https://docs.cosmos.network/cometbft/latest/api-reference/rpc/info/block)
    """
    params = {'height': height} if height is not None else None
    return await self.result('/block', params=params, result_adapter=block_adapter, validate=validate)

