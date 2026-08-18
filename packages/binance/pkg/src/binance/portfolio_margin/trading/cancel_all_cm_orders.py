from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmCancelAllCmOpenOrders(TypedDict):
  """Cancel all active LIMIT orders on specific symbol."""

  code: NotRequired[int]
  """Code."""
  msg: NotRequired[str]
  """Msg."""


class CancelAllCmOrders(RpcEndpoint):
  """Cancel All CM Open Orders"""

  async def cancel_all_cm_orders(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> PmCancelAllCmOpenOrders:
    """Cancel all active LIMIT orders on specific symbol.

    Args:
      symbol: Symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#cancel-all-cm-open-orders)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = PmCancelAllCmOpenOrders
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/papi/v1/cm/allOpenOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
