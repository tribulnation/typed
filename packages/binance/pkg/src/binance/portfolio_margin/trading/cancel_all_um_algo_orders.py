from typing_extensions import Any
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CancelAllUmAlgoOrders(RpcEndpoint):
  """Cancel All UM Algo Open Orders"""

  async def cancel_all_um_algo_orders(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> dict[str, Any]:
    """Cancel All UM Algo Open Orders.

    Args:
      symbol: Symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#cancel-all-um-algo-open-orders)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = dict[str, Any]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/papi/v1/um/algo/allOpenOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
