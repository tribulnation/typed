from json import dumps
from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BatchCancelResult(TypedDict):
  """One cancelled order from a batch cancel."""

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
  fee: NotRequired[str]
  """Fee."""
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


class BatchOrdersCancel(RpcEndpoint):
  """Cancel multiple orders. At least one of orderIds/clientOrderIds must be sent."""

  async def batch_orders_cancel(
    self,
    *,
    symbol: str,
    order_ids: list[int] | None = None,
    client_order_ids: list[str] | None = None,
    validate: bool | None = None,
  ) -> list[BatchCancelResult]:
    """Cancel multiple orders. At least one of orderIds/clientOrderIds must be sent.

    Args:
      symbol: Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000).
      order_ids: Order ID list.
      client_order_ids: Client order ID list.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/trade#cancel-multiple-option-orders)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_ids is not None:
      params['orderIds'] = dumps(order_ids, separators=(',', ':'))
    if client_order_ids is not None:
      params['clientOrderIds'] = dumps(client_order_ids, separators=(',', ':'))
    _Response = list[BatchCancelResult]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/eapi/v1/batchOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
