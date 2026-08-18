from typing_extensions import AsyncIterator, Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class SpotAlgoHistoricalOrder(TypedDict):
  """One spot Algo order."""

  algoId: int
  """Algo order identifier."""
  symbol: str
  """Trading symbol."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  totalQty: str
  """Total order quantity, in the base asset."""
  executedQty: str
  """Executed quantity so far, in the base asset."""
  executedAmt: str
  """Executed notional amount so far, in the quote asset."""
  avgPrice: str
  """Average execution price so far."""
  clientAlgoId: str
  """Client-supplied (or server-generated) unique Algo order identifier."""
  bookTime: Timestamp
  """Time the order was booked."""
  endTime: Timestamp
  """Time the order finished (0 while still working)."""
  algoStatus: str
  """Algo order status. Documented values include `WORKING`, `DONE`, `CANCELLED`, `FAILED`, but the venue does not declare this as a closed enum."""
  algoType: str
  """Algo strategy. Documented examples are `TWAP` and `VP`, but the venue does not declare this as a closed enum."""
  urgency: Literal['LOW', 'MEDIUM', 'HIGH']
  """Execution urgency selected at order time."""


class SpotAlgoHistoricalOrders(TypedDict):
  """Historical (finished or cancelled) Algo orders."""

  total: int
  """Number of historical Algo orders returned."""
  orders: list[SpotAlgoHistoricalOrder]
  """Historical Algo orders."""


class HistoricalOrders(RpcEndpoint):
  """Query Historical Algo Orders (USER_DATA)"""

  async def historical_orders(
    self,
    *,
    symbol: str | None = None,
    side: Literal['SELL', 'BUY'] | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> SpotAlgoHistoricalOrders:
    """Get historical (finished or cancelled) spot TWAP orders.

    Args:
      symbol: Trading symbol, e.g. BNBUSDT.
      side: Order side.
      start_time: Start of the query window, UTC ms.
      end_time: End of the query window, UTC ms.
      page: Page number, 1-indexed.
      page_size: Records per page. Range [1, 100]. The venue documents this parameter as a string; specced as `integer` since it is arithmetic input to pagination (spec-authoring rule 7).

    References:
      - [Official docs](https://developers.binance.com/docs/algo/spot-algo/Query-Historical-Algo-Orders)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if side is not None:
      params['side'] = side
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if page is not None:
      params['page'] = page
    if page_size is not None:
      params['pageSize'] = page_size
    _Response = SpotAlgoHistoricalOrders
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/algo/spot/historicalOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def historical_orders_paged(
    self,
    *,
    symbol: str | None = None,
    side: Literal['SELL', 'BUY'] | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[SpotAlgoHistoricalOrders]:
    """Yield successive pages of `historical_orders`.

    Requests `page` from 1 upwards and stops once it has covered the `total` items the
    response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.historical_orders(
        symbol=symbol,
        side=side,
        start_time=start_time,
        end_time=end_time,
        page_size=page_size,
        page=page,
        validate=validate,
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
