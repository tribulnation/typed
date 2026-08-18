"""`DELETE /api/v1/hf/orders` — Cancel All Orders By Symbol."""

from typing_extensions import Literal
from typed_core.validation import validator
from kucoin.core import RpcEndpoint


_Type = Literal['success']
adapter = validator[_Type](_Type)  # type: ignore


class CancelAllBySymbol(RpcEndpoint):
  """`Cancel All Orders By Symbol` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.cancel_all_by_symbol`."""

  async def cancel_all_by_symbol(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> Literal['success']:
    """Cancel every open spot hf order for one trading pair. Sends cancellation requests only -- confirm via Get Open Orders or the private order WebSocket feed.

    Args:
      symbol: Trading pair symbol to cancel every open order for.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.authed_request(
      'DELETE',
      '/api/v1/hf/orders',
      params=params,
      validator=adapter,
      validate=validate,
    )
