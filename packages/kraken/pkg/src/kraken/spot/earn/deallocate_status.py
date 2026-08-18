"""`spot.earn.deallocate_status` -- private Spot endpoint."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class EarnDeallocateStatusResult(TypedDict):
  pending: NotRequired[bool]
  """`true` if a deallocation operation is still in progress on this strategy."""


_deallocate_status_type = EarnDeallocateStatusResult | None
validate_deallocate_status = validator[_deallocate_status_type](_deallocate_status_type)  # type: ignore


class DeallocateStatus(RpcEndpoint):
  """`spot.earn.deallocate_status`."""

  async def deallocate_status(
    self,
    strategy_id: str,
  ) -> EarnDeallocateStatusResult | None:
    """Get the status of the last deallocation request.

    Requires either the `Earn Funds` or `Query Funds` API key permission.

    (De)allocation operations are asynchronous, and this endpoint lets the client retrieve the status of the last dispatched operation. There can be only one (de)allocation request in progress for a given user and strategy.

    The `pending` attribute in the response indicates whether the previously dispatched operation is still in progress (`true`) or has completed (`false`). If the dispatched request failed with an error, the HTTP error is returned to the client as if it belonged to this request.

    Specific errors within the `Earnings` error class this method can return:
    - Insufficient funds: `EEarnings:Insufficient funds:Insufficient funds to complete the (de)allocation request`
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`

    Args:
      strategy_id: ID of the Earn strategy, from `spot.earn.strategies`.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/earn/get-deallocation-status)
    """
    data: dict = {
      'strategy_id': strategy_id,
    }

    return await self.authed_request(
      '/0/private/Earn/DeallocateStatus', data, validator=validate_deallocate_status
    )
