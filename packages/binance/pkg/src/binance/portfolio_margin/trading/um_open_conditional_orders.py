from typing_extensions import Any
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UmOpenConditionalOrders(RpcEndpoint):
  """Query All Current UM Open Conditional Orders"""

  async def um_open_conditional_orders(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> dict[str, Any]:
    """Get all open conditional orders on a symbol. Weight: - 1 for a single `symbol` - 40 when `symbol` is omitted Security Type: USER_DATA Notes: - If `symbol` is not provided, conditional open orders for all symbols are returned. Args: symbol (Optional[str] = None): recv_window (Optional[int] = None): Returns: ApiResponse[QueryAllCurrentUmOpenConditionalOrdersResponse] Raises: RequiredError: If a required parameter is missing.

    Args:
      symbol: Trading pair symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-all-current-um-open-conditional-orders)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = dict[str, Any]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/um/conditional/openOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
