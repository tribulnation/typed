from typing_extensions import Any
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CancelAllMarginOrders(RpcEndpoint):
  """Cancel Margin Account All Open Orders on a Symbol"""

  async def cancel_all_margin_orders(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> dict[str, Any]:
    """Cancel Margin Account All Open Orders on a Symbol.

    Args:
      symbol: Symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#cancel-margin-account-all-open-orders-on-asymbol)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = dict[str, Any]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/papi/v1/margin/allOpenOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
