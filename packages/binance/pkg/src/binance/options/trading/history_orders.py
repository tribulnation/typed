from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class HistoryOrder(TypedDict):
  """One finished order (status CANCELLED, FILLED or REJECTED)."""

  orderId: NotRequired[int]
  """System order number."""
  symbol: NotRequired[str]
  """Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000)."""
  price: NotRequired[str]
  """Order price."""
  quantity: NotRequired[str]
  """Order quantity."""
  executedQty: NotRequired[str]
  """Quantity executed so far."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Buy/sell direction."""
  type: NotRequired[Literal['LIMIT']]
  """Order type."""
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'GTX']]
  """Time-in-force method."""
  reduceOnly: NotRequired[bool]
  """Whether the order is reduce-only."""
  createTime: NotRequired[Timestamp]
  """Order creation time."""
  updateTime: NotRequired[Timestamp]
  """Last update time."""
  status: NotRequired[
    Literal['ACCEPTED', 'PARTIALLY_FILLED', 'CANCELLED', 'FILLED', 'REJECTED']
  ]
  """Order status."""
  avgPrice: NotRequired[str]
  """Average price of completed trade."""
  clientOrderId: NotRequired[str]
  """Client order ID."""
  priceScale: NotRequired[int]
  """Price precision."""
  quantityScale: NotRequired[int]
  """Quantity precision."""
  optionSide: NotRequired[Literal['CALL', 'PUT']]
  """Option side."""
  quoteAsset: NotRequired[str]
  """Quote asset."""
  mmp: NotRequired[bool]
  """Whether this is a market-maker-protection order."""


class HistoryOrders(RpcEndpoint):
  """Query all finished orders within the last 5 days (status CANCELLED, FILLED or REJECTED)."""

  async def history_orders(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[HistoryOrder]:
    """Query all finished orders within the last 5 days (status CANCELLED, FILLED or REJECTED).

    Args:
      symbol: Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000).
      order_id: Order ID.
      start_time: Start time.
      end_time: End time.
      limit: Number of result sets returned.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/trade#query-option-order-history)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[HistoryOrder]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/eapi/v1/historyOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
