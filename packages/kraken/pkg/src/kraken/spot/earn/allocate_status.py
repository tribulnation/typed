"""`spot.earn.allocate_status` -- private Spot endpoint."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class EarnAllocateStatusResult(TypedDict):
  pending: NotRequired[bool]
  """`true` if a allocation operation is still in progress on this strategy."""


_allocate_status_type = EarnAllocateStatusResult | None
validate_allocate_status = validator[_allocate_status_type](_allocate_status_type)  # type: ignore


class AllocateStatus(RpcEndpoint):
  """`spot.earn.allocate_status`."""

  async def allocate_status(self, strategy_id: str) -> EarnAllocateStatusResult | None:
    """Get the status of the last allocation request.

    Requires either the `Earn Funds` or `Query Funds` API key permission.

    (De)allocation operations are asynchronous, and this endpoint lets the client retrieve the status of the last dispatched operation. There can be only one (de)allocation request in progress for a given user and strategy.

    The `pending` attribute in the response indicates whether the previously dispatched operation is still in progress (`true`) or has completed (`false`). If the dispatched request failed with an error, the HTTP error is returned to the client as if it belonged to this request.

    Specific errors within the `Earnings` error class this method can return:
    - Insufficient funds: `EEarnings:Insufficient funds:Insufficient funds to complete the (de)allocation request`
    - User cap exceeded: `EEarnings:Above max:The allocation exceeds user limit for the strategy`
    - Total cap exceeded: `EEarnings:Above max:The allocation exceeds the total strategy limit`
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`

    Args:
      strategy_id: ID of the Earn strategy, from `spot.earn.strategies`.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/earn/get-allocation-status)
    """
    data: dict = {
      'strategy_id': strategy_id,
    }

    return await self.authed_request(
      '/0/private/Earn/AllocateStatus', data, validator=validate_allocate_status
    )
