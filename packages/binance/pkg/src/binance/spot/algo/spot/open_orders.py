from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class SpotAlgoOrder(TypedDict):
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


class SpotAlgoOpenOrders(TypedDict):
  """Currently working Algo orders."""

  total: int
  """Number of open Algo orders returned."""
  orders: list[SpotAlgoOrder]
  """Open Algo orders."""


class OpenOrders(RpcEndpoint):
  """Query Current Algo Open Orders (USER_DATA)"""

  async def open_orders(self, *, validate: bool | None = None) -> SpotAlgoOpenOrders:
    """Get all open spot TWAP orders.

    References:
      - [Official docs](https://developers.binance.com/docs/algo/spot-algo/Query-Current-Algo-Open-Orders)
    """
    _Response = SpotAlgoOpenOrders
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/algo/spot/openOrders', validator=_validator, validate=validate
    )
