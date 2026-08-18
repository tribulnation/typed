"""`GET /api/v1/stop-order/{orderId}` — spot.stop_orders.get_by_order_id."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class StopOrder(TypedDict):
  id: str
  """Stop order id."""
  symbol: str
  """Trading pair."""
  userId: str
  """Owning account's user id."""
  status: Literal['NEW', 'TRIGGERED']
  """Stop order status."""
  type: Literal['limit', 'market']
  """Order type submitted once the stop triggers."""
  side: Literal['buy', 'sell']
  """Order side."""
  price: str
  """Limit price for the order submitted once the stop triggers."""
  size: str
  """Order quantity, in the base currency."""
  funds: str | None
  """Order value in the quote currency, for a `market`-type triggered order; `null` for `limit`."""
  stp: Literal['CN', 'CO', 'CB', 'DC'] | None
  """Self-trade prevention strategy in effect, or `null` when none was requested."""
  timeInForce: Literal['GTC', 'GTT', 'IOC', 'FOK']
  """Time-in-force rule for the order submitted once the stop triggers."""
  cancelAfter: int
  """Seconds until the triggered order is automatically cancelled when `timeInForce` is `GTT`; `-1` means never."""
  postOnly: bool
  """Whether the triggered order is post-only."""
  hidden: bool
  """Whether the triggered order would be hidden from the order book. KuCoin discontinued Hidden Orders as of 2026-08-03; this remains a response field but is no longer a settable request parameter."""
  iceberg: bool
  """Whether the triggered order would be an iceberg order. Discontinued as a request parameter as of 2026-08-03; see `hidden`."""
  visibleSize: str | None
  """Visible portion of an iceberg order once triggered; `null` since Hidden Orders were discontinued."""
  channel: str
  """Order submission channel, e.g. `API`."""
  clientOid: str
  """Caller-assigned order id passed at creation time."""
  remark: str
  """Order remark passed at creation time."""
  tags: str | None
  """Order source tag, or `null` when none applies."""
  relatedNo: str | None
  """Related order id, if this stop order is linked to another order; `null` otherwise. Undocumented by KuCoin beyond the field name -- always `null` in this pass's live capture, since the captured order was a standalone stop order."""
  orderTime: int
  """Time the stop order was placed, accurate to nanoseconds."""
  domainId: str
  """Originating domain, e.g. `kucoin`."""
  tradeSource: Literal['USER', 'MARGIN_SYSTEM']
  """Who placed the order."""
  tradeType: Literal['TRADE', 'MARGIN_TRADE', 'MARGIN_ISOLATED_TRADE']
  """Trading account the order was placed on."""
  feeCurrency: str
  """Currency the trading fee is charged in."""
  takerFeeRate: str
  """Taker fee rate applied to this order."""
  makerFeeRate: str
  """Maker fee rate applied to this order."""
  createdAt: Timestamp
  """Time the stop order was created."""
  stop: Literal['loss', 'entry']
  """Stop order trigger type."""
  stopTriggerTime: Timestamp | None
  """Time the stop condition triggered; `null` while the order is still `NEW`."""
  stopPrice: str
  """Trigger price."""
  limitPrice: str | None
  """Undocumented by KuCoin beyond the field name (present in the official SDK's list-item model, absent from its single-order model, but observed on both in live captures). Always `null` in this pass's captures; presumed related to a triggered order's resulting limit price."""
  pop: str | None
  """Undocumented by KuCoin beyond the field name. Always `null` in this pass's captures."""
  activateCondition: str | None
  """Undocumented by KuCoin beyond the field name. Always `null` in this pass's captures."""


_Type = StopOrder
adapter = validator[_Type](_Type)  # type: ignore


class GetByOrderId(RpcEndpoint):
  """`spot.stop_orders.get_by_order_id` — mixed into `StopOrders`, the product exposing `spot.stop_orders.get_by_order_id`."""

  async def get_by_order_id(
    self,
    order_id: str,
    *,
    validate: bool | None = None,
  ) -> StopOrder:
    """Get a single stop order's full details by the venue-assigned order id.

    Args:
      order_id: Stop order id to look up, as returned by Add Stop Order or Get Stop Orders List.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'GET',
      f'/api/v1/stop-order/{order_id}',
      validator=adapter,
      validate=validate,
    )
