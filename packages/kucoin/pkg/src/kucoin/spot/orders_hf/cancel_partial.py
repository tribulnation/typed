"""`DELETE /api/v1/hf/orders/cancel/{orderId}` — Cancel Partial Order."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class HfCancelPartialOrderResult(TypedDict):
  """Quantity accepted for cancellation from the order."""

  orderId: str
  """System-generated id of the order."""
  cancelSize: str
  """Quantity cancelled."""


_Type = HfCancelPartialOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelPartial(RpcEndpoint):
  """`Cancel Partial Order` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.cancel_partial`."""

  async def cancel_partial(
    self,
    order_id: str,
    *,
    symbol: str,
    cancel_size: str,
    validate: bool | None = None,
  ) -> HfCancelPartialOrderResult:
    """Cancel part of a single spot hf order's remaining unfilled quantity, leaving the rest resting.

    Args:
      order_id: System-generated id of the order to partially cancel.
      symbol: Trading pair symbol the order belongs to.
      cancel_size: Quantity to cancel from the order's remaining unfilled size.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
      'cancelSize': cancel_size,
    }
    return await self.authed_request(
      'DELETE',
      f'/api/v1/hf/orders/cancel/{order_id}',
      params=params,
      validator=adapter,
      validate=validate,
    )
