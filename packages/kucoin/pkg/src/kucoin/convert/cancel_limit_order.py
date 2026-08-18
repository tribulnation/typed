"""`DELETE /api/v1/convert/limit/order/cancel` — Cancel Convert Limit Order."""

from typed_core.validation import TypedDict
from kucoin.core import RpcEndpoint


class ConvertCancelLimitOrder(TypedDict):
  """Identifies the convert limit order to cancel."""

  clientOrderId: str
  """Client-chosen order id from the order's placement."""


class CancelLimitOrder(RpcEndpoint):
  """`Cancel Convert Limit Order` — mixed into `Convert`, the product exposing `convert.cancel_limit_order`."""

  async def cancel_limit_order(
    self,
    convert_cancel_limit_order: ConvertCancelLimitOrder,
    *,
    validate: bool | None = None,
  ) -> None:
    """Cancel a resting convert limit order by its client order id.

    Args:
      convert_cancel_limit_order: Order to cancel.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    await self.authed_request(
      'DELETE',
      '/api/v1/convert/limit/order/cancel',
      json=convert_cancel_limit_order,
      validate=validate,
    )
