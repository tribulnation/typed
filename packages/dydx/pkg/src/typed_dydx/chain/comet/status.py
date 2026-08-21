"""Comet status endpoint."""

from pydantic import TypeAdapter

from typed_dydx.chain.comet.core import CometEndpoint
from typed_dydx.chain.comet.types import StatusResponse


status_adapter = TypeAdapter(StatusResponse)


class Status(CometEndpoint):
  """Comet status endpoint group."""

  async def status(self, validate: bool | None = None) -> StatusResponse:
    """Return Comet node health, sync state, and validator info.

    Args:
      validate: Validation override for this request.

    Returns:
      Node status result.

    References:
      - [CometBFT RPC docs](https://docs.cosmos.network/cometbft/latest/api-reference/rpc/info/status)
    """
    return await self.result('/status', result_adapter=status_adapter, validate=validate)

