"""`POST /api/v1/copy-trade/futures/orders/test` — Add Order Test."""

from typed_core.validation import validator
from kucoin.types import (
  CopyTradeAddOrderLimit,
  CopyTradeAddOrderMarket,
  CopyTradeAddOrderResult,
)
from kucoin.core import RpcEndpoint


_Type = CopyTradeAddOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class AddOrderTest(RpcEndpoint):
  """`Add Order Test` — mixed into `CopyTrading`, the product exposing `copy_trading.add_order_test`."""

  async def add_order_test(
    self,
    body: CopyTradeAddOrderLimit | CopyTradeAddOrderMarket,
    *,
    validate: bool | None = None,
  ) -> CopyTradeAddOrderResult:
    """Validate a copy-trading order placement request -- parameters, signature -- without ever entering the matching engine. An order placed through this endpoint cannot be queried afterwards by any other endpoint. Requires the API key's `LeadtradeFutures` permission.

    Args:
      body: Order placement parameters, identical to Add Order.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/copy-trade/futures/orders/test',
      json=body,
      validator=adapter,
      validate=validate,
    )
