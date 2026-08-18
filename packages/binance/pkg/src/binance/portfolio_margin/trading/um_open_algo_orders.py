from typing_extensions import Any
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UmOpenAlgoOrders(RpcEndpoint):
  """Query All Current UM Open Algo Orders"""

  async def um_open_algo_orders(
    self,
    *,
    algo_type: str | None = None,
    symbol: str | None = None,
    algo_id: int | None = None,
    validate: bool | None = None,
  ) -> dict[str, Any]:
    """Get all UM open algo orders on a symbol. If the symbol is not sent, orders for all symbols will be returned.

    Args:
      algo_type: Algo order type.
      symbol: Trading pair symbol.
      algo_id: Algo order id to act on.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-all-current-um-open-algo-orders)
    """
    params = {}
    if algo_type is not None:
      params['algoType'] = algo_type
    if symbol is not None:
      params['symbol'] = symbol
    if algo_id is not None:
      params['algoId'] = algo_id
    _Response = dict[str, Any]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/um/algo/openAlgoOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
