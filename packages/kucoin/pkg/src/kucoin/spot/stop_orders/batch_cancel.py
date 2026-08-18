"""`DELETE /api/v1/stop-order/cancel` — spot.stop_orders.batch_cancel."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BatchCancelStopOrdersResult(TypedDict):
  cancelledOrderIds: list[str]
  """Ids of the stop orders successfully cancelled by this call."""


_Type = BatchCancelStopOrdersResult
adapter = validator[_Type](_Type)  # type: ignore


class BatchCancel(RpcEndpoint):
  """`spot.stop_orders.batch_cancel` — mixed into `StopOrders`, the product exposing `spot.stop_orders.batch_cancel`."""

  async def batch_cancel(
    self,
    *,
    symbol: str,
    trade_type: Literal['TRADE', 'MARGIN_TRADE', 'MARGIN_ISOLATED_TRADE'],
    order_ids: str,
    validate: bool | None = None,
  ) -> BatchCancelStopOrdersResult:
    """Cancel multiple untriggered stop orders in a single request, scoped to a trading pair and trade type and optionally narrowed to a specific list of order ids.

    Args:
      symbol: Trading pair to cancel open stop orders for.
      trade_type: Trading account the targeted orders were placed on.
      order_ids: Comma-separated stop order ids to cancel.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
      'tradeType': trade_type,
      'orderIds': order_ids,
    }
    return await self.authed_request(
      'DELETE',
      '/api/v1/stop-order/cancel',
      params=params,
      validator=adapter,
      validate=validate,
    )
