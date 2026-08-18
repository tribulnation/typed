"""`POST /api/v1/stop-order` — spot.stop_orders.add."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class AddStopOrderRequest(TypedDict):
  clientOid: str
  """Unique order id created by the caller (a UUID is recommended) -- numbers, letters, underscores and hyphens only, up to 40 characters. Returned back on the order and usable to look it up; never reuse a `clientOid` across requests."""
  symbol: str
  """Trading pair, e.g. `BTC-USDT`."""
  side: Literal['buy', 'sell']
  """Order side."""
  type: Literal['limit', 'market']
  """Order type submitted once the stop triggers. `limit` requires `price` and `size`; `market` takes `size` or `funds` (not both) and no `price`."""
  price: NotRequired[str]
  """Limit price for the order submitted once the stop triggers. Required when `type` is `limit`; unused for `market`. Must be a multiple of the trading pair's `priceIncrement`."""
  stopPrice: str
  """Trigger price. Once the market reaches this price, the order is submitted to the matching engine as a regular `type` order."""
  size: NotRequired[str]
  """Order quantity, in the base currency, submitted once the stop triggers. Required when `type` is `limit`; for `market`, either `size` or `funds` is given, not both. Must be a positive multiple of the trading pair's `baseIncrement`, between `baseMinSize` and `baseMaxSize`."""
  funds: NotRequired[str]
  """Order value, in the quote currency, submitted once the stop triggers. Only valid when `type` is `market`, as an alternative to `size`."""
  remark: NotRequired[str]
  """Order placement remark, up to 20 ASCII characters."""
  stp: NotRequired[Literal['CN', 'CO', 'CB', 'DC']]
  """Self-trade prevention strategy."""
  timeInForce: NotRequired[Literal['GTC', 'GTT', 'IOC', 'FOK']]
  """Time-in-force rule for the order submitted once the stop triggers. Only meaningful when `type` is `limit`."""
  cancelAfter: NotRequired[int]
  """Seconds until the triggered order is automatically cancelled, when `timeInForce` is `GTT`. `-1` (the default) never cancels automatically."""
  postOnly: NotRequired[bool]
  """Reject the triggered order instead of taking liquidity, rather than resting it. Disabled when `timeInForce` is `IOC` or `FOK`."""
  tradeType: NotRequired[Literal['TRADE', 'MARGIN_TRADE', 'MARGIN_ISOLATED_TRADE']]
  """Trading account the order draws on."""


class AddStopOrderResult(TypedDict):
  orderId: str
  """Unique id generated for the new stop order, usable for later Get/Cancel calls."""


_Type = AddStopOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class Add(RpcEndpoint):
  """`spot.stop_orders.add` — mixed into `StopOrders`, the product exposing `spot.stop_orders.add`."""

  async def add(
    self,
    add_stop_order_request: AddStopOrderRequest,
    *,
    validate: bool | None = None,
  ) -> AddStopOrderResult:
    """Place a stop order into the Spot trading system. The order rests untriggered until the market reaches `stopPrice`, at which point it is submitted to the matching engine as a regular limit or market order. Maximum 20 untriggered stop orders per trading pair per account.

    Args:
      add_stop_order_request: Stop order placement parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/stop-order',
      json=add_stop_order_request,
      validator=adapter,
      validate=validate,
    )
