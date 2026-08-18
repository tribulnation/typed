from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CancelAllResult(TypedDict):
  """Acknowledgement of a cancel-all request."""

  code: NotRequired[int]
  """Result code."""
  msg: NotRequired[str]
  """Result message."""


class AllOpenOrdersCancel(RpcEndpoint):
  """Cancel all active orders on a symbol."""

  async def all_open_orders_cancel(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> CancelAllResult:
    """Cancel all active orders on a symbol.

    Args:
      symbol: Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000).

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/trade#cancel-all-option-orders-on-specific-symbol)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = CancelAllResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/eapi/v1/allOpenOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
