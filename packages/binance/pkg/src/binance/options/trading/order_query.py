from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class OrderStatus(TypedDict):
  """Current status of one order."""

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
  selfTradePreventionMode: NotRequired[
    Literal['NONE', 'EXPIRE_TAKER', 'EXPIRE_MAKER', 'EXPIRE_BOTH']
  ]
  """Self-trade prevention mode."""


class OrderQuery(RpcEndpoint):
  """Check an order's status. An order will not be found if its status is CANCELED or REJECTED, it has no filled trade, AND it was created more than 3 days ago."""

  async def order_query(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    client_order_id: str | None = None,
    validate: bool | None = None,
  ) -> OrderStatus:
    """Check an order's status. An order will not be found if its status is CANCELED or REJECTED, it has no filled trade, AND it was created more than 3 days ago.

    Args:
      symbol: Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000).
      order_id: Order ID.
      client_order_id: User-defined order ID.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/trade#query-single-order)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if client_order_id is not None:
      params['clientOrderId'] = client_order_id
    _Response = OrderStatus
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/eapi/v1/order', params=params, validator=_validator, validate=validate
    )
