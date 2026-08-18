from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class CancelFuturesSweepResponse(TypedDict):
  """Result of cancelling the pending futures sweep."""

  success: bool
  """Whether the sweep cancellation succeeded."""


@dataclass(frozen=True, kw_only=True)
class Cancel(RpcEndpoint):
  """`DELETE /api/v3/brokerage/cfm/sweeps`."""

  async def cancel(self) -> CancelFuturesSweepResponse:
    """Cancel the pending sweep from the CFM futures wallet to the USD spot wallet, if any. A sweep already processing cannot be cancelled.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/futures/cancel-pending-futures-sweep)
    """
    return await self.authed_request(
      'DELETE',
      '/api/v3/brokerage/cfm/sweeps',
      validator=validator(CancelFuturesSweepResponse),
    )
