from typing_extensions import AsyncIterator, Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class SpotAlgoSubOrder(TypedDict):
  """One child order routed by an Algo order."""

  algoId: int
  """Parent Algo order identifier."""
  orderId: int
  """Exchange order identifier of this child order."""
  orderStatus: str
  """Child order status. Documented example is `FILLED`; the venue does not declare this as a closed enum."""
  executedQty: str
  """Executed quantity of this child order, in the base asset."""
  executedAmt: str
  """Executed notional amount of this child order, in the quote asset."""
  feeAmt: str
  """Fee charged on this child order (negative)."""
  feeAsset: str
  """Asset the fee was charged in."""
  bookTime: Timestamp
  """Time this child order was booked."""
  avgPrice: str
  """Average execution price of this child order."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  symbol: str
  """Trading symbol."""
  subId: int
  """Sequence number of this child order within the parent Algo order."""
  timeInForce: str
  """Time-in-force of this child order. Documented example is `IMMEDIATE_OR_CANCEL`; the venue does not declare this as a closed enum."""
  origQty: str
  """Original requested quantity of this child order, in the base asset."""


class SpotAlgoSubOrders(TypedDict):
  """Child orders routed by one Algo order."""

  total: int
  """Number of child orders returned."""
  executedQty: str
  """Total executed quantity across all child orders, in the base asset."""
  executedAmt: str
  """Total executed notional amount across all child orders, in the quote asset."""
  subOrders: list[SpotAlgoSubOrder]
  """Child orders."""


class SubOrders(RpcEndpoint):
  """Query Sub Orders (USER_DATA)"""

  async def sub_orders(
    self,
    *,
    algo_id: int,
    page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> SpotAlgoSubOrders:
    """Get the child orders routed by a specified spot Algo order.

    Args:
      algo_id: Parent Algo order identifier.
      page: Page number, 1-indexed.
      page_size: Records per page. Range [1, 100]. The venue documents this parameter as a string; specced as `integer` since it is arithmetic input to pagination (spec-authoring rule 7).

    References:
      - [Official docs](https://developers.binance.com/docs/algo/spot-algo/Query-Sub-Orders)
    """
    params: dict = {
      'algoId': algo_id,
    }
    if page is not None:
      params['page'] = page
    if page_size is not None:
      params['pageSize'] = page_size
    _Response = SpotAlgoSubOrders
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/algo/spot/subOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def sub_orders_paged(
    self,
    *,
    algo_id: int,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[SpotAlgoSubOrders]:
    """Yield successive pages of `sub_orders`.

    Requests `page` from 1 upwards and stops once it has covered the `total` items the
    response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.sub_orders(
        algo_id=algo_id, page_size=page_size, page=page, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or page_size is None or pages * page_size >= total:
        break
      page += 1
