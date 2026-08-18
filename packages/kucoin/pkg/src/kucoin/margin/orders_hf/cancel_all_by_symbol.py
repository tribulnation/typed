"""`DELETE /api/v3/hf/margin/orders` — Cancel All Orders By Symbol."""

from typing_extensions import Literal
from typed_core.validation import validator
from kucoin.core import RpcEndpoint


_Type = Literal['success']
adapter = validator[_Type](_Type)  # type: ignore


class CancelAllBySymbol(RpcEndpoint):
  """`Cancel All Orders By Symbol` — mixed into `OrdersHf`, the product exposing `margin.orders_hf.cancel_all_by_symbol`."""

  async def cancel_all_by_symbol(
    self,
    *,
    symbol: str,
    trade_type: str,
    validate: bool | None = None,
  ) -> Literal['success']:
    """Cancel every open margin hf order for one trading pair and margin mode. Sends cancellation requests only -- confirm via Get Open Orders or the private order WebSocket feed.

    Args:
      symbol: Trading pair symbol to cancel every open order for.
      trade_type: Margin mode to cancel orders in. KuCoin's own examples show `MARGIN_TRADE` (cross); `MARGIN_ISOLATED_TRADE` (isolated) is the sibling value confirmed live on this subdivision's read endpoints, but this endpoint's own docs page never states the field is a closed set, so it is left as a plain string rather than a guessed enum.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
      'tradeType': trade_type,
    }
    return await self.authed_request(
      'DELETE',
      '/api/v3/hf/margin/orders',
      params=params,
      validator=adapter,
      validate=validate,
    )
