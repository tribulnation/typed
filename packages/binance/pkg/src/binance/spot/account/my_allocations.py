from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SorAllocation(TypedDict):
  """One allocation resulting from SOR order placement."""

  symbol: str
  """Symbol this allocation was made on."""
  allocationId: int
  """Allocation ID assigned by Binance."""
  allocationType: Literal['SOR']
  """Type of allocation."""
  orderId: int
  """ID of the order this allocation belongs to."""
  orderListId: int
  """ID of the order list this allocation's order belongs to, or -1 if it is not part of one."""
  price: str
  """Allocation price, as a decimal string."""
  qty: str
  """Allocation quantity, as a decimal string."""
  quoteQty: str
  """Quote asset quantity for this allocation, as a decimal string."""
  commission: str
  """Commission charged on this allocation, as a decimal string."""
  commissionAsset: str
  """Asset the commission was charged in."""
  time: int
  """Millisecond timestamp the allocation was made."""
  isBuyer: bool
  """Whether this account was the buyer in the allocation."""
  isMaker: bool
  """Whether this account was the maker in the allocation."""
  isAllocator: bool
  """Whether this account was the allocator (the SOR order's owner) in the allocation."""


class MyAllocations(RpcEndpoint):
  """Query allocations"""

  async def my_allocations(
    self,
    *,
    symbol: str,
    start_time: int | None = None,
    end_time: int | None = None,
    from_allocation_id: int | None = None,
    limit: int | None = None,
    order_id: int | None = None,
    validate: bool | None = None,
  ) -> list[SorAllocation]:
    """Retrieve allocations resulting from SOR (Smart Order Routing) order placement. The time between `startTime` and `endTime` can't be longer than 24 hours. Supported parameter combinations: `symbol` (allocations from oldest to newest); `symbol` + `startTime` (oldest allocations since `startTime`); `symbol` + `endTime` (newest allocations until `endTime`); `symbol` + `startTime` + `endTime` (allocations within the time range); `symbol` + `fromAllocationId` (allocations by allocation ID); `symbol` + `orderId` (allocations related to an order, starting with oldest); `symbol` + `orderId` + `fromAllocationId` (allocations related to an order, by allocation ID).

    Args:
      symbol: Symbol to query.
      start_time: Start of the time range, in milliseconds.
      end_time: End of the time range, in milliseconds.
      from_allocation_id: Allocation ID to fetch from (inclusive).
      limit: Maximum number of allocations to return.
      order_id: Order ID to filter allocations by.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
    """
    params: dict = {
      'symbol': symbol,
    }
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if from_allocation_id is not None:
      params['fromAllocationId'] = from_allocation_id
    if limit is not None:
      params['limit'] = limit
    if order_id is not None:
      params['orderId'] = order_id
    _Response = list[SorAllocation]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/api/v3/myAllocations',
      params=params,
      validator=_validator,
      validate=validate,
    )
