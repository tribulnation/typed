from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMCountdownCancelAllResult(TypedDict):
  """The countdown that was set."""

  symbol: str
  """Symbol."""
  countdownTime: str
  """Countdown cancellation time in milliseconds."""


class AutoCancelAllOpenOrders(RpcEndpoint):
  """Auto-Cancel All Open Orders"""

  async def auto_cancel_all_open_orders(
    self,
    *,
    symbol: str,
    countdown_time: int,
    validate: bool | None = None,
  ) -> CoinMCountdownCancelAllResult:
    """Cancel all open orders of the given symbol after the specified countdown elapses, as an outage safety net. Call this repeatedly as a heartbeat — each call replaces any pending countdown for the symbol. Binance checks all countdowns approximately every 10ms. A `countdownTime` of 0 stops the countdown.

    Args:
      symbol: Symbol.
      countdown_time: Countdown duration in milliseconds before all open orders on `symbol` are canceled. 0 stops any pending countdown.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#auto-cancel-all-open-orders)
    """
    params: dict = {
      'symbol': symbol,
      'countdownTime': countdown_time,
    }
    _Response = CoinMCountdownCancelAllResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/dapi/v1/countdownCancelAll',
      params=params,
      validator=_validator,
      validate=validate,
    )
