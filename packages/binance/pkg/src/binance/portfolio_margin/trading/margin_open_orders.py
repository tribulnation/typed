from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmCurrentMarginOpenOrder(TypedDict):
  """PmCurrentMarginOpenOrder."""

  clientOrderId: NotRequired[str]
  """Client Order ID."""
  cummulativeQuoteQty: NotRequired[str]
  """Cummulative Quote Qty."""
  executedQty: NotRequired[str]
  """Executed Qty."""
  icebergQty: NotRequired[str]
  """Iceberg Qty."""
  isWorking: NotRequired[bool]
  """Is Working."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  origQty: NotRequired[str]
  """Orig Qty."""
  price: NotRequired[str]
  """Price."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Side."""
  status: NotRequired[str]
  """Enum：completed，processing."""
  stopPrice: NotRequired[str]
  """please ignore when order type is TRAILING_STOP_MARKET."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  time: NotRequired[Timestamp]
  """Event time."""
  timeInForce: NotRequired[str]
  """Time In Force."""
  type: NotRequired[str]
  """Normal order type after trigger if appliable."""
  updateTime: NotRequired[Timestamp]
  """last update time."""
  accountId: NotRequired[int]
  """Account ID."""
  selfTradePreventionMode: NotRequired[str]
  """self trading preventation mode."""
  preventedMatchId: NotRequired[str]
  """Prevented Match ID."""
  preventedQuantity: NotRequired[str]
  """Prevented Quantity."""


class MarginOpenOrders(RpcEndpoint):
  """Query Current Margin Open Order"""

  async def margin_open_orders(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> list[PmCurrentMarginOpenOrder]:
    """Query Current Margin Open Order.

    Args:
      symbol: Symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-current-margin-open-order)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = list[PmCurrentMarginOpenOrder]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/margin/openOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
